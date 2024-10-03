import requests

response = requests.post("https://fast-api-luc-kkk-a60fa2188ae5.herokuapp.com/ML_Price_Prediction_Getaround", json={
  "model_key": "Audi",
  "mileage": 175096,
  "engine_power": 160,
  "fuel": "diesel",
  "paint_color": "blue",
  "car_type": "estate",
  "private_parking_available": False,
  "has_gps": False,
  "has_air_conditioning": False,
  "automatic_car": False,
  "has_getaround_connect": False,
  "has_speed_regulator": False,
  "winter_tires": False
})
print(response.json())