import os
import json
import pygrib
import numpy as np

class GribProcessor:
    def __init__(self, run_folder: str):
        self.run_folder = run_folder
        self.run_info = self._load_run_info()
    
    def _load_run_info(self):
        info_path = os.path.join(self.run_folder, "run_info.json")
        with open(info_path, "r") as f:
            return json.load(f)

    def list_grib_files(self):
        return [f for f in os.listdir(self.run_folder) if f.endswith(".grib2")]

    def extract_data_arrays(self):
        """Return list of (timestamp, np.ndarray, metadata) for the run."""
        result = []
        for file in self.list_grib_files():
            path = os.path.join(self.run_folder, file)
            grbs = pygrib.open(path)
            grb = grbs[1]  # or custom selection logic
            data, lats, lons = grb.data()
            result.append((grb.validDate, data, {
                "units": grb.units,
                "name": grb.name,
                "shortName": grb.shortName,
            }))
        return result

    def convert_to_images(self, output_dir: str, colormap="Blues"):
        import matplotlib.pyplot as plt
        os.makedirs(output_dir, exist_ok=True)

        for timestamp, data, meta in self.extract_data_arrays():
            plt.figure()
            plt.imshow(data, cmap=colormap)
            plt.colorbar(label=meta["units"])
            plt.title(f"{meta['name']} - {timestamp}")
            filename = os.path.join(output_dir, f"{timestamp}.png")
            plt.savefig(filename)
            plt.close()
