# meteo

download_data.py :
crée un dossier raw_data avec des sous dossier, rain, etc... et dans chaque sous dossier les données brutes sous forme de csv pour les 24h qui arrivent

process_data.py
process les données brutes pour générer les cartes

	commande :
	python3 process_data.py [lat] [lon] [radius(km)] [raw_data_path] [type(rain,temp,clouds)] [type] ...

	example :
	python3 process_data.py 43.6 1.44 100 raw_data rain temp
