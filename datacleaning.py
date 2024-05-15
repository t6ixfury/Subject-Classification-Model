import pandas as pd

data = pd.read_csv('ComputerScienceArticles-Main.csv')


subjects = ['Computer Vision and Pattern Recognition', 
            'Machine Learning', 
            'Computation and Language', 
            'Robotics']

data.loc[~data['Subject'].isin(subjects), 'Subject'] = 'Other'


data.to_csv("TrainingData.csv")
