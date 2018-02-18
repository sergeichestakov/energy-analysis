import keras
import os
import sys
import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.wrappers.scikit_learn import KerasClassifier

class EnergyModel:

    energy_data = os.path.abspath(os.path.curdir) + '/data/recs2009_public.csv'
    columns = 'columns.txt'
    INPUT = [
    'TOTCSQFT',
    'ACROOMS',
    'BEDROOMS',
    'WASHLOAD',
    'USECENAC',
    'NCOMBATH',
    'TYPEHUQ',
    'TEMPHOME',
    'CENACHP',
    'TEMPNITEAC',
    'SWIMPOOL',
    'NUMCFAN',
    'MAINTAC',
    'COOLTYPE',
    ]

    OUTPUT = ['KWH'] #Total Energy consumed in KWH
    TRAIN_ENTRIES = 9000 #Remainder is test (12083 Total)

    def __init__(self):
        self.model = self.train()

    def train(self):
        df = pd.read_csv(EnergyModel.energy_data, low_memory=False)

        self.trainX = df[EnergyModel.INPUT][0:EnergyModel.TRAIN_ENTRIES]
        self.testX = df[EnergyModel.INPUT][EnergyModel.TRAIN_ENTRIES:]

        self.trainY = df[EnergyModel.OUTPUT][0:EnergyModel.TRAIN_ENTRIES]
        self.testY = df[EnergyModel.OUTPUT][EnergyModel.TRAIN_ENTRIES:]

        self.resetOutliers()

        #Normalize data
        self.trainXScaled = self.normalize(self.trainX)
        self.trainYScaled = self.normalize(self.trainY)

        self.testXScaled = self.normalize(self.testX)

        #Initialize and train model
        model = self.createModel()
        model.fit(self.trainXScaled, self.trainYScaled, batch_size=15, epochs=5, verbose=1)

        return model


    #Construct Neural Network model
    def createModel(self, optimizer='sgd'):
        model = Sequential()

        model.add(Dense(32, input_dim=len(EnergyModel.INPUT), activation='relu'))
        model.add(Dense(16))
        model.add(Dense(8, activation='softmax'))
        model.add(Dense(5))
        model.add(Dense(1, activation='sigmoid'))

        model.compile(loss='mean_squared_error', optimizer=optimizer)

        return model

    #Predicts energy consumption based on user submitted input
    def predict(self, inputVector):
        print(inputVector)
        scaledInput = self.normalize(inputVector)
        #scaledInput = inputVector
        print(scaledInput)
        results = self.model.predict(scaledInput, verbose=1)

        prediction = self.denormalize(self.testY, results[0]).item()
        return prediction

    #Predict and output results from test set
    def output(self):
        results = self.model.predict(self.testXScaled, verbose=1)
        length = len(self.testY)
        sum = 0
        for index in range(length):
            output = self.testY.values[index][0]
            prediction = self.denormalize(self.testY, results[index]).item()
            sum += abs(output - prediction)
            #print('OUTPUT: ', output)
            #print('PREDICTION: ', prediction, '\n')

        print('Average Error: ', sum / length)
        print(self.model.summary())

    def resetOutliers(self):
        #Reset nonzero values and outliers
        self.trainX[self.trainX < 0] = 0
        self.trainY[self.trainY < 0] = 0

        self.testX[self.testX < 0] = 0
        self.testY[self.testY < 0] = 0

        self.trainY[self.trainY > 20000] = 20000
        self.testY[self.testY > 20000] = 20000

    #Normalize all values in array to between 0 and 1
    def normalize(self,rawpoints, high=1.0, low=0.0):
        print(rawpoints)
        mins = np.min(rawpoints, axis=0)
        maxs = np.max(rawpoints, axis=0)
        rng = maxs - mins
        print(rng)
        indices = rng == 0
        rng[indices] = 1
        res = (rawpoints - mins) / rng
        return res

    #Return normalized values back to original
    def denormalize(self, original, target):
        mins = np.min(original, axis=0)
        maxs = np.max(original, axis=0)

        return target * (maxs - mins) + mins

if __name__ == '__main__':
    model = EnergyModel()
    model.output()
