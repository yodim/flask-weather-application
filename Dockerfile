FROM python:3.7-alpine

RUN apk update && apk upgrade

RUN apk add --no-cache sqlite

RUN apk --no-cache add musl-dev linux-headers g++

RUN apk add --update --no-cache curl-dev libressl-dev

RUN python3 -m pip install --upgrade pip 

WORKDIR /app

COPY . .

RUN ls /app

RUN pip3 install -r requirements.txt
    
EXPOSE 5000

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]