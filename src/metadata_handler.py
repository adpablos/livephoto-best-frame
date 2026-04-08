from datetime import datetime
import os
import piexif
from pathlib import Path
import logging
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

class MetadataHandler:
    """Base class for handling file metadata operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_creation_time(self, file_path: Path) -> datetime:
        """Get creation time using appropriate method based on file type"""
        if self._is_video(file_path):
            return self._get_video_creation_time(file_path)
        elif self._is_image(file_path):
            return self._get_image_creation_time(file_path)
        else:
            return self._get_file_creation_time(file_path)

    def _is_video(self, file_path: Path) -> bool:
        """Check if file is a video"""
        return file_path.suffix.lower() in ['.mov', '.mp4']

    def _is_image(self, file_path: Path) -> bool:
        """Check if file is an image"""
        return file_path.suffix.lower() in ['.jpg', '.jpeg']

    def _get_video_creation_time(self, file_path: Path) -> datetime:
        """Get creation time from video file"""
        methods = [
            self._try_hachoir_metadata,
            self._get_file_creation_time,
        ]
        return self._try_methods(file_path, methods)

    def _get_image_creation_time(self, file_path: Path) -> datetime:
        """Get creation time from image file"""
        try:
            exif_dict = piexif.load(str(file_path))
            if "Exif" in exif_dict:
                date_bytes = exif_dict["Exif"].get(piexif.ExifIFD.DateTimeOriginal)
                if date_bytes:
                    date_str = date_bytes.decode('ascii')
                    return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
        except Exception as e:
            self.logger.debug(f"Failed to get EXIF creation time: {str(e)}")
        
        return self._get_file_creation_time(file_path)

    def _get_file_creation_time(self, file_path: Path) -> datetime:
        """Get creation time from file system"""
        stats = file_path.stat()
        timestamps = [
            stats.st_birthtime if hasattr(stats, 'st_birthtime') else float('inf'),
            stats.st_ctime,
            stats.st_mtime,
        ]
        earliest = min(t for t in timestamps if t != float('inf'))
        return datetime.fromtimestamp(earliest)

    def _try_methods(self, file_path: Path, methods) -> datetime:
        """Try multiple methods to get creation time"""
        for method in methods:
            try:
                result = method(file_path)
                if result:
                    return result
            except Exception as e:
                self.logger.debug(f"Method {method.__name__} failed: {str(e)}")
        return datetime.now()

    def update_file_timestamps(self, file_path: Path, creation_time: datetime, 
                             modified_time: datetime = None) -> None:
        """Update file timestamps ensuring creation time is set correctly"""
        if modified_time is None:
            modified_time = datetime.now()
            
        # Read file content
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Remove existing file
        os.remove(file_path)
        
        # Create new file with original content
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Set creation time first
        os.utime(file_path, (creation_time.timestamp(), creation_time.timestamp()))
        
        # Then set modified time
        os.utime(file_path, (creation_time.timestamp(), modified_time.timestamp()))

    def update_exif_dates(self, file_path: Path, date_time: datetime) -> None:
        """Update EXIF date fields with proper encoding handling"""
        try:
            date_str = date_time.strftime("%Y:%m:%d %H:%M:%S")
            
            # First, remove existing EXIF data
            try:
                piexif.remove(str(file_path))
            except:
                pass
            
            # Create minimal EXIF dictionary with only date fields
            exif_dict = {
                "0th": {
                    piexif.ImageIFD.DateTime: date_str.encode('ascii')
                },
                "Exif": {
                    piexif.ExifIFD.DateTimeOriginal: date_str.encode('ascii'),
                    piexif.ExifIFD.DateTimeDigitized: date_str.encode('ascii')
                }
            }
            
            # Insert new EXIF data
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, str(file_path))
            
        except Exception as e:
            self.logger.error(f"Failed to update EXIF dates: {str(e)}")
            # Continue with file timestamps even if EXIF update fails

    def _try_hachoir_metadata(self, video_path: Path) -> datetime | None:
        """Try to get creation time using hachoir"""
        parser = createParser(str(video_path))
        if parser:
            with parser:
                metadata = extractMetadata(parser)
                if metadata and metadata.has('creation_date'):
                    return metadata.get('creation_date')
        return None

    def copy_metadata_to_image(self, source_path: Path, image_path: Path) -> None:
        """Copy metadata from source file to image"""
        try:
            # Get original creation time
            original_time = self.get_creation_time(source_path)
            # Get current time for modified timestamp
            current_time = datetime.now()
            
            # Format datetime for EXIF
            date_str = original_time.strftime("%Y:%m:%d %H:%M:%S")
            
            # Create EXIF dictionary
            exif_dict = {
                "0th": {
                    piexif.ImageIFD.DateTime: date_str.encode('ascii')
                },
                "Exif": {
                    piexif.ExifIFD.DateTimeOriginal: date_str.encode('ascii'),
                    piexif.ExifIFD.DateTimeDigitized: date_str.encode('ascii'),
                }
            }
            
            # Primero creamos el archivo con la fecha original
            with open(image_path, 'rb') as f:
                img_data = f.read()
            
            # Eliminamos el archivo existente
            os.remove(image_path)
            
            # Creamos uno nuevo con los timestamps originales
            with open(image_path, 'wb') as f:
                f.write(img_data)
            
            # Establecemos la fecha original para ambos timestamps
            os.utime(image_path, (original_time.timestamp(), original_time.timestamp()))
            
            # Insertamos los metadatos EXIF
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, str(image_path))
            
            # Finalmente actualizamos solo la fecha de modificación
            os.utime(image_path, (original_time.timestamp(), current_time.timestamp()))
            
            self.logger.info(
                f"Metadata copied to {image_path}. "
                f"Creation time: {original_time}, "
                f"Modified time: {current_time}"
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to copy metadata: {str(e)}") 