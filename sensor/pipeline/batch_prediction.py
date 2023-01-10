from sensor.entity.config_entity import DataValidationConfig
from sensor.exception import SensorException
from sensor.predictor import ModelResolver
from sensor.entity import config_entity
from sensor.utils import load_object
from sensor.logger import logging
from datetime import datetime
from sensor import utils
import pandas as pd
import numpy as np
import os,sys

PREDICTION_DIR= "prediction"
VALIDATION_DIR= "validation_report"


def start_batch_prediction(input_file_path):
    try:
        os.makedirs(PREDICTION_DIR,exist_ok=True)
        report_file_dir = os.path.join(PREDICTION_DIR, VALIDATION_DIR)
        os.makedirs(report_file_dir, exist_ok=True)

        logging.info("Creating model resolver object")
        model_resolver = ModelResolver(model_registry="saved_models")   # Location where models are saved
        logging.info(f"Reading file :{input_file_path}")
        df = pd.read_csv(input_file_path)
        logging.info("Replace na value in input df")
        df.replace({"na":np.NAN},inplace=True)
        
        # Validation
        try:
            pass
            #report_file_name = f"report{datetime.now().strftime('%m%d%Y__%H%M%S')}.yaml"



        except Exception as e:
            raise SensorException(e, sys)

        # Loading transformer
        logging.info("Loading transformer to transform dataset")
        transformer = load_object(file_path=model_resolver.get_latest_transformer_path())
        
        # Getting input features
        input_feature_names =  list(transformer.feature_names_in_)
        # data frame
        input_arr = transformer.transform(df[input_feature_names])

        # Prediction    
        logging.info("Loading model to make prediction")
        model = load_object(file_path=model_resolver.get_latest_model_path())
        prediction = model.predict(input_arr)

        # Target decoding   
        logging.info("Target encoder to convert predicted column into categorical")
        target_encoder = load_object(file_path=model_resolver.get_latest_target_encoder_path())

        cat_prediction = target_encoder.inverse_transform(prediction)

        df["prediction"]=prediction
        df["cat_pred"]=cat_prediction

        logging.info('Creating prediction file with time stamp')
        # Creating file name for predition with time stamp by replacing .csv
        prediction_file_name = os.path.basename(input_file_path).replace(".csv",f"{datetime.now().strftime('%m%d%Y__%H%M%S')}.csv")
        # Creating directory to save prediction file
        prediction_file_path = os.path.join(PREDICTION_DIR,prediction_file_name)
        # Saving the df to directory
        df.to_csv(prediction_file_path,index=False,header=True)
        return prediction_file_path
    except Exception as e:
        raise SensorException(e, sys)
