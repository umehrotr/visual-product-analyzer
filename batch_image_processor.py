import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
from typing import List, Dict
from tqdm import tqdm
from visual_product_analyzer import VisualProductAnalyzer


class BatchImageProcessor:
    def __init__(self):
        self.analyzer = VisualProductAnalyzer()
    
    def process_directory(self, directory_path: str, output_dir: str = "processed"):
        """
        Process all images in a directory
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
        image_files = [
            f for f in Path(directory_path).rglob('*')
            if f.suffix.lower() in image_extensions
        ]
        
        print(f"Found {len(image_files)} images to process")
        
        # Process with progress bar
        results = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.process_single_image, str(img), output_dir): img
                for img in image_files
            }
            
            for future in tqdm(futures, desc="Processing images"):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Error processing {futures[future]}: {e}")
        
        # Create summary report
        self.create_summary_report(results, output_dir)
        
        return results
    
    def process_single_image(self, image_path: str, output_dir: str) -> Dict:
        """
        Process a single image and save results
        """
        try:
            analysis = self.analyzer.analyze_product_image(image_path)
            
            # Save individual result
            output_file = Path(output_dir) / f"{Path(image_path).stem}.json"
            with open(output_file, "w") as f:
                json.dump(analysis, f, indent=2)
            
            return {
                "image": image_path,
                "status": "success",
                "analysis": analysis
            }
        except Exception as e:
            return {
                "image": image_path,
                "status": "error",
                "error": str(e)
            }
    
    def create_summary_report(self, results: List[Dict], output_dir: str):
        """
        Create a summary CSV of all processed images
        """
        import csv
        
        summary_file = Path(output_dir) / "summary_report.csv"
        
        with open(summary_file, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Image", "Status", "Product Type", "Category",
                "Suggested Title", "Confidence"
            ])
            
            for result in results:
                if result["status"] == "success":
                    analysis = result["analysis"]
                    writer.writerow([
                        result["image"],
                        "Success",
                        analysis.get("product_type", ""),
                        analysis.get("category", ""),
                        analysis.get("suggested_title", ""),
                        analysis.get("confidence_score", 0)
                    ])
                else:
                    writer.writerow([
                        result["image"],
                        "Error",
                        "",
                        "",
                        "",
                        0
                    ])
        
        print(f"\n✅ Summary report saved to {summary_file}")
# Usage:
# processor = BatchImageProcessor()
# processor.process_directory("./product_images", "./analysis_output")
