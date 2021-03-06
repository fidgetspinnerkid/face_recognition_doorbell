import face_recognition
import cv2
import numpy as np
import pickle
import time
from twilio.rest import Client


# TODO Change Face Encoding method: Identification faulty (racist)


def box_faces(known_face_encodings=[], known_face_names=[], model="hog"):
    """Displays the image of the given file with a green box around any detected faces
        Returns the locations of the faces like [ (top, right, bottom, left) ]"""
    video_capture = cv2.VideoCapture(0)

    alreadySent = []

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_frame = frame[:, :, ::-1]

        # Find all the faces and face encodings in the frame of video
        face_locations = face_recognition.face_locations(rgb_frame, model=model)

        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        faces = []

        # Loop through each face in this frame of video
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            name = "Unknown"

            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                best_match = int(np.argmin([abs(x) for x in distances]))
                name = known_face_names[best_match]

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            faces.append(name)

            for name, lastTime in alreadySent:
                if time.time() - lastTime >= 20:
                    alreadySent.remove((name, lastTime))

            peopleToSend = []
            for face in faces:
                if face not in [x[0] for x in alreadySent]:
                    peopleToSend.append(face)
                    alreadySent.append((face, time.time()))
            # notify_user(peopleToSend)

        # Display the resulting image
        cv2.imshow('Video', frame)
        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # once stream is done
    video_capture.release()
    cv2.destroyAllWindows()


def notify_user(people):
    print("sending text")
    if 'Unknown' in people:
        # Your Account Sid and Auth Token from twilio.com/console
        account_sid = ''
        auth_token = ''
        client = Client(account_sid, auth_token)

        client.messages.create(
            body='There is a stranger among you',
            from_='+',
            to='+'
        )
    elif people == []:
        return
    else:
        account_sid = ''
        auth_token = ''
        client = Client(account_sid, auth_token)
        client.messages.create(
            body=format_list_of_names(people),
            from_='',
            to=''
        )


def format_list_of_names(names):
    retStr = ""
    if len(names) == 2:
        return names[0] + " and " + names[1] + " are at your door."
    elif len(names) == 1:
        return names[0] + " is at your door."
    else:
        for name in names[:-1]:
            retStr += name + ", "
        retStr += " and " + names[len(names)]
        return retStr


if __name__ == '__main__':
    data = pickle.loads(open("encodings\encodings.pickle", "rb").read())
    # print(data)
    known_encodings = data["encodings"]

    known_names = data["names"]

    box_faces(known_encodings, known_names, model="cnn")
