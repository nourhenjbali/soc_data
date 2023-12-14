import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# Define governorates globally
governorates = [
    "Ariana", "Béja", "Ben Arous", "Bizerte", "Jendouba","Sfax",
    "Kef", "Manouba", "Nabeul", "Tunis", "Zaghouan","Sidi Bouzid",
    "Kairouan", "Kasserine", "Siliana", "Sousse", "Monastir",
    "Mahdia", "Gafsa", "Gabes", "Medenine", "Tozeur", "Kebili", "Tataouine"
]

def scrape_accident_data():
    url = "https://news-tunisia.tunisienumerique.com/tunisia/road-accident/"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        post_elements = soup.find_all("li", class_="infinite-post")

        accidents = []
        for idx, post_element in enumerate(post_elements, start=1):
            link_element = post_element.find("a")
            text_div = post_element.find("div", class_="archive-list-text")
            title_element = text_div.find("h2")
            description_element = text_div.find("p")

            link = link_element['href'] if link_element else ""
            title = title_element.text.strip() if title_element else ""
            description = description_element.text.strip() if description_element else ""

            accidents.append({'id': idx, 'link': link, 'title': title, 'description': description})

        return accidents
    else:
        print("Échec de récupération de la page web. Code d'état :", response.status_code)
        return None

def find_governorate(title):
    lower_title = title.lower()
    for governorate in governorates:
        if governorate.lower() in lower_title:
            return governorate
    return None

def insert_into_mongodb(collection, accidents):
    # Insertion des données dans la collection accidents
    for accident in accidents:
        # Add the 'location' field to the accident document
        location = find_governorate(accident['title'])
        accident['location'] = location.lower() if location else None
    collection.insert_many(accidents)

def main():
    # Connexion à la base de données MongoDB
    connection_string = 'mongodb+srv://nourhenjebali:nourhen@soc.9qnt9so.mongodb.net/bookapp?retryWrites=true&w=majority'
    client = MongoClient(connection_string)

    # Spécifiez le nom de la base de données et de la collection
    db = client.get_database('bookapp')  # Remplacez 'accident_database' par le nom de votre base de données
    collection = db.get_collection('accidents')  # Remplacez 'accidents' par le nom de votre collection

    # Récupérer les données
    accident_data = scrape_accident_data()
    if accident_data:
        for accident in accident_data:
            print(f"ID: {accident['id']}")
            print(f"Link: {accident['link']}")
            print(f"Title: {accident['title']}")
            print(f"Description: {accident['description']}")
            print("\n")

        # Ajouter les données à MongoDB
        insert_into_mongodb(collection, accident_data)
    
        # Function to find the governorate in a title
        for idx, title in enumerate(accident_data, start=1):
            location = find_governorate(title['title'])
            print(f"Article {idx} : Location: {location}")

    # Fermer la connexion à MongoDB
    client.close()

if __name__ == "__main__":
    main()
