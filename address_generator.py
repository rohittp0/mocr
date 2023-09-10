import random


# Function to generate a random Malayalam word
def generate_malayalam_word(length):
    malayalam_alphabet = 'ംഅആഇഈഉഊഋഎഏഐഒഓഔകഗഘങചഛജഝഞടഠഡഢണതഥദധനപഫബഭമയരലവശഷസഹാിീുൂൃെേൈൊോൌ്'
    return ''.join(random.choice(malayalam_alphabet) for _ in range(length))


# Function to generate a Malayalam house address
def generate_malayalam_address():
    house_number_present = random.choice([True, False])

    if house_number_present:
        house_number = f"{random.randint(1, 100)}/{random.randint(1, 100)}"
    else:
        house_number = ''

    house_name_length = random.randint(4, 20)
    house_name = generate_malayalam_word(house_name_length)

    # Combine the house number and name
    address = f"{house_number} {house_name}"

    # Add a tilde (~) if the address exceeds 12 characters
    if len(address) > 12:
        address = address[:12] + "~" + address[12:]

    return address


# Generate and append 13,000 Malayalam house addresses to "house.txt"
with open("texts/house.txt", "a", encoding="utf-8") as file:
    for _ in range(13000):
        address = generate_malayalam_address()
        file.write(address + "\n")

print("Addresses appended to 'house.txt'")
