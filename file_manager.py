"""
File Manager Utility
Handles date-stamped CSV and HTML file generation
Only creates one file per day based on the date stamp
"""

import os
from datetime import datetime
import pandas as pd


class DateStampedFileManager:
    """Manages date-stamped CSV and HTML files"""
    
    def __init__(self, output_dir='output'):
        """
        Initialize file manager
        
        Args:
            output_dir: Directory to store output files
        """
        self.output_dir = output_dir
        self.today = datetime.now().strftime('%Y-%m-%d')
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"✓ Created output directory: {self.output_dir}")
    
    def get_csv_filename(self, prefix='portfolio_analysis'):
        """
        Get CSV filename with today's date stamp
        
        Args:
            prefix: Prefix for the filename
            
        Returns:
            str: Filename with date stamp
        """
        return os.path.join(self.output_dir, f"{prefix}_{self.today}.csv")
    
    def get_html_filename(self, prefix='portfolio_analysis'):
        """
        Get HTML filename with today's date stamp
        
        Args:
            prefix: Prefix for the filename
            
        Returns:
            str: Filename with date stamp
        """
        return os.path.join(self.output_dir, f"{prefix}_{self.today}.html")
    
    def csv_exists_for_today(self, prefix='portfolio_analysis'):
        """
        Check if CSV file already exists for today
        
        Args:
            prefix: Prefix for the filename
            
        Returns:
            bool: True if file exists, False otherwise
        """
        filename = self.get_csv_filename(prefix)
        return os.path.exists(filename)
    
    def save_to_csv(self, df, prefix='portfolio_analysis', append=True):
        """
        Save DataFrame to CSV with date stamp
        Appends to existing file by default, creating new file if it doesn't exist
        
        Args:
            df: pandas DataFrame to save
            prefix: Prefix for the filename
            append: If True, appends to existing file; if False, overwrites
            
        Returns:
            str: Path to saved CSV file
        """
        csv_file = self.get_csv_filename(prefix)
        
        # Add timestamp column if not present
        if 'Timestamp' not in df.columns:
            from datetime import datetime
            df['Timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if os.path.exists(csv_file) and append:
            # Append to existing file without header
            df.to_csv(csv_file, mode='a', header=False, index=False)
            print(f"✓ Data appended to: {csv_file}")
        else:
            # Create new file with header
            df.to_csv(csv_file, index=False)
            print(f"✓ CSV created: {csv_file}")
        
        return csv_file
    
    def save_html(self, html_content, prefix='portfolio_analysis', force=False):
        """
        Save HTML content with date stamp
        Only saves once per day unless force=True
        
        Args:
            html_content: HTML string to save
            prefix: Prefix for the filename
            force: If True, overwrites existing file
            
        Returns:
            str: Path to saved HTML file or None if skipped
        """
        html_file = self.get_html_filename(prefix)
        
        if os.path.exists(html_file) and not force:
            print(f"ℹ️  HTML file already exists for today: {html_file}")
            print(f"   Skipping HTML generation (use force=True to overwrite)")
            return html_file
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ HTML saved: {html_file}")
        return html_file
    
    def list_files(self, prefix='portfolio_analysis', file_type='csv'):
        """
        List all files with the given prefix and type
        
        Args:
            prefix: Prefix to filter files
            file_type: 'csv' or 'html'
            
        Returns:
            list: List of matching files sorted by date (newest first)
        """
        extension = f".{file_type}"
        files = []
        
        if os.path.exists(self.output_dir):
            for filename in os.listdir(self.output_dir):
                if filename.startswith(prefix) and filename.endswith(extension):
                    filepath = os.path.join(self.output_dir, filename)
                    files.append(filepath)
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return files
    
    def get_latest_file(self, prefix='portfolio_analysis', file_type='csv'):
        """
        Get the most recent file with the given prefix and type
        
        Args:
            prefix: Prefix to filter files
            file_type: 'csv' or 'html'
            
        Returns:
            str: Path to latest file or None if no files found
        """
        files = self.list_files(prefix, file_type)
        return files[0] if files else None
    
    def cleanup_old_files(self, prefix='portfolio_analysis', keep_days=30):
        """
        Remove files older than specified days
        
        Args:
            prefix: Prefix to filter files
            keep_days: Number of days to keep files
            
        Returns:
            int: Number of files deleted
        """
        deleted_count = 0
        cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        
        for file_type in ['csv', 'html']:
            files = self.list_files(prefix, file_type)
            for filepath in files:
                if os.path.getmtime(filepath) < cutoff_time:
                    os.remove(filepath)
                    deleted_count += 1
                    print(f"🗑️  Deleted old file: {filepath}")
        
        return deleted_count


# Made with Bob