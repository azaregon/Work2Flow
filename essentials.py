import requests
from typing import List


apikey = "8dc7a808b2a1a36ad6eb182953a5badc-1654a412-3bba5548"

def send_email(to_:List[str],subject:str,msg:str):
    print("eaakdsajd")
  		# "https://api.mailgun.net/v3/sandboxab5ae0a6ed814a2792f2b2bb93c90555.mailgun.org/messages",
    snd = requests.post(
        "https://api.mailgun.net/v3/mg.rm-dev.my.id/messages",
  		auth=("api", apikey),
  		data={"from": "[NO REPLY] <mailgun@mg.rm-dev.my.id>",
  			"to": to_,
  			"subject": subject,
  			"text": msg})
    print(snd)
    return snd




if __name__ == '__main__':
    # print(send_email( ["dump.truck.aja@gmail.com","aazawarfare.tugas@gmail.com"] ,"LAS","Haloo").status_code)
    pass