from fileinput import filename
from operator import itemgetter
from re import I, X
import string
from tkinter import W
import token
from IPython.display import display
from PIL import Image
import random
import json
import os

os.system('cls' if os.name=='nt' else 'clear')

def create_new_image(all_images, config):
    new_image = {}
    for layer in config["layers"]:
      new_image[layer["name"]] = random.choices(layer["values"], layer["weights"])[0]

    for incomp in config["incompatibilities"]:
      for attr in new_image:
        if new_image[incomp["layer"]] == incomp["value"] and new_image[attr] in incomp["incompatible_with"]:
          return create_new_image(all_images, config)

    if new_image in all_images:
      return create_new_image(all_images, config)
    else:
      return new_image

def generate_unique_images(amount, config):
  print("Generating {} unique NFTs...".format(amount))
  pad_amount = len(str(amount))
  trait_files = {
  }
  for trait in config["layers"]:
    trait_files[trait["name"]] = {}
    for x, key in enumerate(trait["values"]):
      trait_files[trait["name"]][key] = trait["filename"][x]

  all_images = []
  for i in range(amount):
    new_trait_image = create_new_image(all_images, config)
    all_images.append(new_trait_image)

  i = 1
  for item in all_images:
      item["tokenId"] = i
      i += 1

  for i, token in enumerate(all_images):
    attributes = []
    for key in token:
      if key != "tokenId":
        attributes.append({"trait_type": key, "value": token[key]})

#Edit Token Metadata Here
    token_metadata = {
        "name":  config["name"] + str(token["tokenId"]).zfill(pad_amount),
        "symbol": config["symbol"],
        "description": config["description"],
        "seller_fee_basis_points": config["fee"],
        "image": config["baseURI"] + "/images/" + str(token["tokenId"]) + '.png',
        "attributes": attributes,
         "properties":{
            "creators" : [{"address" : "HAhri3YyDyg5ZmzYmr7niMAohL5CbnbspwbvfcFHAVZA", "share": 100}],
            "files" : [{'uri': '{}.png'.format(i + 1),"type" : "image/png"}],
        },
         "collection": config["collection"],
        }

    with open('./metadata/' + str(token["tokenId"]) + '.json', 'w') as outfile:
        json.dump(token_metadata, outfile, indent=4)


  with open('./metadata/all-objects.json', 'w') as outfile:
    json.dump(all_images, outfile, indent=4)

# Image Generation

  for item in all_images:
    layers = []
    for index, attr in enumerate(item):
      if attr != 'tokenId':
        layers.append([])
        layers[index] = Image.open(f'{config["layers"][index]["trait_path"]}/{trait_files[attr][item[attr]]}.png').convert('RGBA')

    if len(layers) == 1:
      rgb_im = layers[0].convert('RGB')
      file_name = str(item["tokenId"]) + ".png"
      rgb_im.save("./images/" + file_name)
    elif len(layers) == 2:
      main_composite = Image.alpha_composite(layers[0], layers[1])
      rgb_im = main_composite.convert('RGB')
      file_name = str(item["tokenId"]) + ".png"
      rgb_im.save("./images/" + file_name)
    elif len(layers) >= 3:
      main_composite = Image.alpha_composite(layers[0], layers[1])
      layers.pop(0)
      layers.pop(0)
      for index, remaining in enumerate(layers):
        main_composite = Image.alpha_composite(main_composite, remaining)
      rgb_im = main_composite.convert('RGB')
      file_name = str(item["tokenId"]) + ".png"
      rgb_im.save("./images/" + file_name)

  # v1.0.2 addition
  token_metadata['properties']['files'][0]['uri'] = str(token["tokenId"]) + '.png'
  print("\nUnique NFT's generated. If you are uploading images to IPFS, please paste the CID below.\nOtherwise, hit ENTER or CTRL+C to quit.")
  cid = input("IPFS Image CID (): ")
  if len(cid) > 0:
    if not cid.startswith("ipfs://"):
      cid = "ipfs://{}".format(cid)
    if cid.endswith("/"):
      cid = cid[:-1]
    for i, item in enumerate(all_images):
      with open('./metadata/' + str(item["tokenId"]) + '.json', 'r') as infile:
        original_json = json.loads(infile.read())
        original_json["image"] = original_json["image"].replace(config["baseURI"]+"/", cid+"/")
       
        with open('./metadata/' + str(item["tokenId"]) + '.json', 'w') as outfile:
          json.dump(original_json, outfile, indent=4)

generate_unique_images(30, {
  "layers": [
    {
      "name": "Background",
      "values": ["Blue", "Orange", "Purple", "Red", "Yellow"],
      "trait_path": "./trait-layers/backgrounds",
      "filename": ["blue", "orange", "purple", "red", "yellow"],
      "weights": [20,20,20,20,20]
    },
    {
      "name": "Face",
      "values": ["White", "Black"],
      "trait_path": "./trait-layers/face",
      "filename": ["face1", "face2"],
      "weights": [50,50]
    },
    {
      "name": "Hair",
      "values": ['Up Hair', 'Down Hair', 'Mohawk', 'Red Mohawk', 'Orange Hair'],
      "trait_path": "./trait-layers/hair",
      "filename": ["hair1", "hair2", "hair3", "hair4", "hair5"],
      "weights": [20,20,20,20,20]
    },
    {
      "name": "Ears",
      "values": ["No Earring", "Left Earring", "Right Earring", "Two Earrings"],
      "trait_path": "./trait-layers/ears",
      "filename": ["ears1", "ears2", "ears3", "ears4"],
      "weights": [25,25,25,25]
    },
    {
      "name": "Eyes",
      "values": ["Regular", "Small", "Rayban", "Hipster", "Focused", "Jalpha", "Jalpha+", "Bottle"],
      "trait_path": "./trait-layers/eyes",
      "filename": ["eyes1", "eyes2", "eyes3", "eyes4", "eyes5", "eyes6", "eyes7", "eyes8"],
      "weights": [20,10,5,1,4,20,10,30]
    },
    {
     "name": "Mouth",
     "values": ["Black Lipstick", "Red Lipstick", "Big Smile", "Smile", "Teeth Smile", "Purple Lipstick"],
     "trait_path": "./trait-layers/mouth",
     "filename": ["mouth1", "mouth2", "mouth3", "mouth4", "mouth5", "mouth6"],
     "weights": [10,10,30,20,15,15,]
    },
    {
     "name": "Beard",
     "values": ["Beard 2", "Beard 3", "Beard 4", "Beard 5", "Beard 6", "Beard 7"],
     "trait_path": "./trait-layers/beard",
     "filename": ["beard1", "beard2", "beard3", "beard4", "beard5", "beard6", "beard7"],
     "weights": [10,10,50,10,15,5]
    },
    {
      "name": "Nose",
      "values": ["Nose", "Nose Ring"],
      "trait_path": "./trait-layers/nose",
      "filename": ["nose1", "nose2"],
      "weights": [50,50]
    }
  ],
  "incompatibilities": [
    {
      "layer": "Background",
      "value": "Blue",
      "incompatible_with": ["Up Hair"]
    },  #  @dev : Blue backgrounds will never have the attribute "Python Logo 2".
  ],
  "baseURI": ".",
  "name": "Player #",
  "symbol": "VR",
  "description": "This is a description for this game.",
  "fee": "500",
  "properties": 
  {
  "creators": [{"address": "N4f6zftYsuu4yT7icsjLwh4i6pB1zvvKbseHj2NmSQw", "share": 100}],
  "files": [{"uri": "0.png", "type": "image/png"}]
  },
  "collection": {"name": "numbers", "family": "numbers"}
}
)
#Additional layer objects can be added following the above formats. They will automatically be composed along with the rest of the layers as long as they are the same size as each other.
#Objects are layered starting from 0 and increasing, meaning the front layer will be the last object. (Branding)
