DROP TABLE IF EXISTS scene CASCADE;
DROP TABLE IF EXISTS characters CASCADE;
DROP TABLE IF EXISTS emotion CASCADE;
DROP TABLE IF EXISTS objects CASCADE;
DROP TABLE IF EXISTS actions CASCADE;
DROP TABLE IF EXISTS location CASCADE;
DROP type IF EXISTS gender;

create type gender as enum ('male', 'female', 'other');



CREATE TABLE Characters 
(
    name VARCHAR(50) NOT NULL,
    gender gender NOT NULL,
    age INTEGER CHECK (age >= 0), 
    id SERIAL PRIMARY KEY
); 
 
CREATE TABLE Emotion 
(  
     emotion_name VARCHAR(50) NOT NULL,
     id SERIAL PRIMARY KEY
); 

CREATE TABLE Objects 
(
    subject_name VARCHAR(50) NOT NULL,
    id SERIAL PRIMARY KEY
); 
 
CREATE TABLE Actions
( 
     act_name VARCHAR(50) NOT NULL,
     subject_id INTEGER REFERENCES Objects(id),
     id SERIAL PRIMARY KEY
); 
 
CREATE TABLE Location
( 
    location_name VARCHAR(50) NOT NULL,
    coordinates VARCHAR(50) NOT NULL,
    safety BOOLEAN NOT NULL,
    id SERIAL PRIMARY KEY
); 

CREATE TABLE Scene
( 
    timess time NOT NULL,
    
    emotion_id INTEGER REFERENCES Emotion(id),
    person_id INTEGER REFERENCES Characters(id),
    location_id INTEGER REFERENCES Location(id),
    action_id INTEGER REFERENCES Actions(id)
); 

 
INSERT INTO Characters (name, gender, age) 
VALUES ('She', 'female', 16), 
       ('Unknown', 'other', 17), 
       ('He', 'male', 13),
       ('Payton', 'female', 25), 
       ('Mary', 'female', 17), 
       ('Sparrow', 'other', 23),
       ('Ethan', 'male', 21),
       ('Sophia', 'female', 18),
       ('Liam', 'male', 25),
       ('Avery', 'other', 19),
       ('Chloe', 'female', 23),
       ('Noah', 'male', 17),
       ('Taylor', 'other', 20),
       ('Isabella', 'female', 22),
       ('Mason', 'male', 24),
       ('Harper', 'female', 26),
       ('Logan', 'male', 19),
       ('Riley', 'other', 18),
       ('Emma', 'female', 21),
       ('Lucas', 'male', 20),
       ('Quinn', 'other', 22); 


INSERT INTO Objects (subject_name) 
VALUES ('loved things'),
       ('known things'),
       ('belongins'),
       ('nothing'); 
 
INSERT INTO Actions (subject_id, act_name) 
VALUES (1, 'love'), 
       (1, 'know'),
       (3, 'see'),
       (2, 'feel'),
       (2, 'mean'),
       (2, 'leave'); 
 
INSERT INTO Emotion (emotion_name) 
VALUES ('fear'), 
       ('loneliness'),
       ('danger'),
       ('leaving home'),
       ('despair'),
       ('unimportant'),
       ('no emotion'); 

INSERT INTO Location (location_name, coordinates, safety)
VALUES ('home', '0,0', TRUE),
       ('Diaspar', '0,0', TRUE),
       ('trail1', '2,0', FALSE),
       ('home2', '1,0', TRUE),
       ('world', '0,0', FALSE),
       ('trail2', '3,0', FALSE); 

INSERT INTO Scene (timess, person_id, emotion_id, action_id, location_id)
VALUES (NOW(), 1, 2, 4, 1), 
       ('10:20:12', 2, 2, 4, 2), 
       ('11:13', 5, 3, 4, 6),
       ('01:20', 3, 2, 6, 5), 
       ('02:27', 2, 2, 4, 3), 
       ('11:13', 5, 3, 4, 6),
       ('01:14', 3, 5, 2, 6),
       ('10:45', 12, 1, 4, 3),
       ('07:32', 6, 3, 1, 2),
       ('11:11', 9, 6, 5, 5),
       (NOW(), 14, 2, 6, 1),
       ('05:20', 1, 7, 3, 4),
       ('06:06', 5, 4, 2, 2),
       ('09:43', 11, 3, 1, 6),
       ('12:00', 2, 1, 4, 5),
       ('04:22', 13, 7, 6, 3),
       ('08:17', 4, 2, 5, 1),
       ('02:49', 10, 6, 3, 2),
       ('06:30', 7, 5, 2, 4),
       ('01:01', 8, 4, 6, 6),
       ('10:10', 15, 1, 1, 5); 