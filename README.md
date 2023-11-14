# meteo

download_data.py :
crée un dossier raw_data avec des sous dossier, rain, etc... et dans chaque sous dossier les données brutes sous forme de csv pour les 24h qui arrivent


process_data.py
process les données brutes pour générer les cartes

	usage: 
	python3 process_data.py [-h] [--lat LAT] [--lon LON] [-r RADIUS] [-d {rain,temp,clouds} [{rain,temp,clouds} ...]]

		options:
		  -h, --help            show this help message and exit
		  --lat LAT             Center latitude (in deg) (default: None)
		  --lon LON             Center longitude (in deg) (default: None)
		  -r RADIUS, --radius RADIUS
		                        Radius (in km) (default: 100)
		  -d {rain,temp,clouds} [{rain,temp,clouds} ...], --data_types {rain,temp,clouds} [{rain,temp,clouds} ...]
		                        Metrics wanted (default: ['rain', 'temp', 'clouds'])

	example :
	python3 process_data.py --lat 43.6 --lon 1.44 -r 100 -d rain temp
