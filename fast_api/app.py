import uvicorn
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import pandas as pd
import mlflow
import json
from typing import Literal, List, Union
import os

description = """
My second great API
# With this app, I can finalized the GETAROUND project
* Enjoy :)
"""

tag_metadata = [
    {
        "name": "Category_1",
        "description": "POST Request"
    },
    {
        "name": "Category_2",
        "description": "GET Request"
    },
    {
        "name": "Category_3",
        "description": "INFERENCE: REAL TIME / BATCH"
    },
    {
        "name": "Category_4",
        "description": "GETAROUND Pricing Prediction (ML)"
    },
    {
        "name": "Category_5",
        "description": "Years Experience - Salary Prediction (ML)"
    }]

app = FastAPI(
    title="🪐 Luc's FAST API V2",
    description=description,
    openapi_tags=tag_metadata)


## new class for blog articles
class BlogArticles(BaseModel):
    title: str
    content: str
    author: str = "Anonymous Author"

    
@app.get("/", tags=["Category_2"])
async def index():
    message = "Hello Luc from my super API"
    return message


@app.get("/blog-articles/{blog_id}", tags=["Category_2"])
async def read_blog_article(blog_id: int):

    articles = pd.read_csv("https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/articles.csv")
    if blog_id > len(articles):
        response = {
            "msg": "We don't have that many articles!"
        }
    else:
        article = articles.iloc[blog_id, :]
        response = {
            "title": article.title,
            "content": article.content, 
            "author": article.author
        }
    return response


@app.post("/create-blog-article", tags=["Category_1"])
async def create_blog_article(blog_article: BlogArticles):
    df = pd.read_csv("https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/articles.csv")
    
    new_article = pd.Series({
        "id": len(df) + 1,
        "title": blog_article.title,
        "content": blog_article.content, 
        "author": blog_article.author
    })
    #df = df.append(new_article, ignore_index=True)
    df = pd.concat([df, new_article], ignore_index=True)
    df.to_csv('new_article.csv')

    return df.to_json()


@app.post("/another-post-endpoint", tags=["Category_1"])
async def another_post_endpoint(blog_article: BlogArticles):
    example_data = {
        'title': blog_article.title,
        'content': blog_article.content,
        'author': blog_article.author
    }
    return example_data


@app.post("/another-post-endpoint-2", tags=["Category_1"])
async def another_post_endpoint_2(blog_article: BlogArticles):
    example_data = pd.Series({
        'title': blog_article.title,
        'content': blog_article.content,
        'author': blog_article.author
    })
    example_data.to_csv('example_data.csv')
    return example_data


@app.post("/batch-prediction", tags=["Category_3"])
async def batch_prediction(file: UploadFile = File(...)):

    return {"Uploaded file name": file.filename}


# new class for pricing prediction
class PredictionPricing(BaseModel):
    model_key: str = "Audi"
    mileage: int = 175096
    engine_power: int = 160
    fuel: str = "diesel"
    paint_color: str = "blue"
    car_type: str = "estate"
    private_parking_available: bool = False
    has_gps: bool = False
    has_air_conditioning: bool = False
    automatic_car: bool = False
    has_getaround_connect: bool = False
    has_speed_regulator: bool = False
    winter_tires: bool = False


@app.post("/ML_Price_Prediction_Getaround", tags=["Category_4"])
async def predict(pricing: PredictionPricing):

    # Read data
    Cars_data = pd.DataFrame(dict(pricing), index=[0])

    # Log model from mlflow
    logged_model = 'runs:/e039ac592e3e4d968e6f1c435fb54c4a/Car_Rental_Price_Predictor'

    # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(logged_model)

    # Predict on a Pandas DataFrame.
    prediction = loaded_model.predict(Cars_data)
    # print(prediction)

    # Format response
    response = {"pricing_euro": str(round(prediction.tolist()[0], 2))}

    return response


## new class for salary prediction
class PredictionFeatures(BaseModel):
    YearsExperience: float

@app.post("/Prediction_Salary", tags=["Category_5"])
async def predict(predictionFeatures: PredictionFeatures):
 
    # Read data 
    years_experience = pd.DataFrame({"YearsExperience": [predictionFeatures.YearsExperience]})

    # # Load model as a PyFuncModel (from mlflow)
    logged_model = 'runs:/5ddb2b536ab74c9aa38be820d7e64b78/salary_estimator'

    # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(logged_model)

    # If you want to load model persisted locally
    #loaded_model = joblib.load('salary_predictor/model.joblib')

    # Predict on a Pandas DataFrame.
    #prediction = loaded_model.predict(pd.DataFrame(years_experience))

    # Predict
    prediction = loaded_model.predict(years_experience)
    # print(prediction)
    # print(prediction.tolist())

    # Format response
    response = {"Prediction (Salary)": prediction.tolist()[0]}
    
    return response


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000) # Here you define your web server to run the `app` variable (which contains FastAPI instance), with a specific host IP (0.0.0.0) and port (4000)
