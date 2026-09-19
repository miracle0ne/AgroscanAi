from PIL import Image
import numpy as np
from .model import Agromodel

class Crop:
  name ="unknown crop"
  diseases=[]
  symptoms=[]
  recommendations=[]
CROP_REGISTER={}
def register_crop(name):
  def decorator(crop_class):
    CROP_REGISTER[name]=crop_class
    return crop_class
  return decorator
  
@register_crop("Maize")
class Maize(Crop):

    name = "Maize"

    diseases = [
        "Possible Maize Leaf Disease"
    ]

    symptoms = [
        "Leaf discoloration",
        "Spots or damaged areas"
    ]

    recommendations = [
        "Inspect nearby maize plants",
        "Consult an agricultural expert"
    ]
@register_crop("Tomato")
class Tomato(Crop):

    name = "Tomato"

    diseases = [
        "Possible Tomato Leaf Disease"
    ]

    symptoms = [
        "Leaf spots",
        "Yellowing leaves"
    ]

    recommendations = [
        "Inspect affected leaves",
        "Consult an agricultural expert"
    ]


@register_crop("Onion")
class Onion(Crop):

    name = "Onion"

    diseases = [
        "Possible Onion Leaf Disease"
    ]

    symptoms = [
        "Leaf discoloration",
        "Drying or damaged leaves"
    ]

    recommendations = [
        "Inspect affected plants",
        "Consult an agricultural expert"
    ]
class CropAgent:
    def __init__(self):
     self.model=Agromodel()

    def getcrop(self, crop_name):

        crop_class = CROP_REGISTER.get(crop_name)

        if crop_class is None:
            return None

        return crop_class()
    def prepare_image(self,image):
      image_object=Image.open(image)
      image_object.load()
      image_object=image_object.resize((224,224))
      image_object =image_object.convert("RGB")
      image_array=np.array(image_object)
      image_array=image_array.astype("float32") /255.0
      image_array=np.expand_dims(image_array,axis=0)
      return image_array      

    def analyze_crop(
        self,
        crop_name,
        image=None,
        mime_type="image/jpeg"
    ):

        crop = self.getcrop(crop_name)

        if crop is None:
            return {
                "error": "crop not supported"
            }

        if image:

            result = self.model.analyze_image(
                image,
                mime_type
            )

            return {
                "crop": crop.name,
                "ai_Analysis": result
            }

        return {
            "crop": crop.name,
            "symptoms": crop.symptoms,
            "recommendations": crop.recommendations,
        }


        crop = self.getcrop(crop_name)

        if crop is None:
            return {
                "error": "crop not supported"
            }

        

        if image:
          result=self.model.analyze_image(image)
          return {
            "crop":crop.name,
            "ai_Analysis":result
          }            
        return {
            "crop": crop.name,
            "symptoms": crop.symptoms,
            "recommendations": crop.recommendations,
            
      }