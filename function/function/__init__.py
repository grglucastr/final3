import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    conn = psycopg2.connect(host='final33dbsrv.postgres.database.azure.com', port="5432", database='techconfdb', 
    user='final33admin@final33dbsrv', password='Senha123')

    cur = conn.cursor()

    try:
        # Get notification message and subject from database using the notification_id
        sql = "select message, subject from notification where id = " + str(notification_id)
        cur.execute(sql)
        notification = cur.fetchone()        

        # Get attendees email and name
        sql = "select * from attendee"
        cur.execute(sql)
        attendees = cur.fetchall()

        # Loop through each attendee and send an email with a personalized subject
        for attendee in attendees:
            message = Mail(
            from_email='georgewrldazr@outlook.com',
            to_emails=attendee[5],
            subject=notification[1],
            html_content='<strong>' + notification[0] + '</strong>')

            try:
                sg = SendGridAPIClient("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")
                sg.send(message)
            except Exception as e:
                print(e.message)

        notifiedmsg = "Notified " + str(len(attendees)) + " attendees"
        
        # Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        sql = "update notification set status = '"+ notifiedmsg +"', completed_date = now() where id = " + str(notification_id)
        cur.execute(sql)
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        cur.close()
        conn.close()