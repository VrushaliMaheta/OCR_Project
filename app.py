from flask import Flask, render_template,request,jsonify
import image_processing as ip
import os


app = Flask(__name__)



ALLOWED_EXTENSIONS= set(['png', 'jpg', 'jpeg'])

# function to check the file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/' , methods=['GET', 'POST'])
def home():
   msg = ""
   text = ""
   status =""
   response={}
   jsonRes ={}
   if request.method == 'POST':
      f = request.files['file']
      f.save(f.filename)
      #print("size",size(os.path.getsize(f.filename)))

      if f and allowed_file(f.filename):
         select = str(request.form.get("doc_type"))
         print("Selected Type ", select)
         global name
         name = f.filename
         #name="./static/images/rotate_img.jpg"
         response = ip.img_pro(name,select)
         if "Doc Type Error" in response:
               status="Failed"
               msg="Uploaded File and Selected Document Miss Metch"
         else:
               status = "Success"
               msg = "Process Success"

      else:
         status="Failed"
         msg = 'Only allow jpg,png'
         response["Doc Type Error"] = 'Invalid file....allow Only jpg,png,jpeg'
   jsonRes = {
      'status': status ,
      'msg': msg,
      'result': response
   }
   print("data",dict(jsonRes))
   res=str(dict(jsonRes))
   return render_template('home.html', doc=res)


if __name__ == '__main__':
   app.run(debug=True)