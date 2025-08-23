from flask import Flask  , render_template , redirect , request , session , flash
from flask_sqlalchemy import SQLAlchemy  
from flask_migrate import Migrate 
from sqlalchemy import and_ , not_ , or_
from sqlalchemy.orm import joinedload
from flask_wtf import FlaskForm 
from wtforms import StringField , SubmitField



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:    @localhost:5432/db2" 
app.config['SQLALCHEMY_CHECK_MODIFICATIONS'] = False 
app.secret_key = 'codeFlou'

db = SQLAlchemy(app) 
mg = Migrate(app , db) 

# table muse

class Muse(db.Model):
    __tablename__ = 'muse'
    id  = db.Column(db.Integer , primary_key = True)
    nom = db.Column(db.String(30), unique = False , nullable = True) 
    province = db.Column(db.String(30), unique = False , nullable = True)

    #relation avec la table user 
    user = db.relationship("User", backref="muse", lazy=True)


#
# muse par defaut information


# table user

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer , primary_key = True) 
    name = db.Column(db.String(30), nullable  =True , unique = False)
    email = db.Column(db.String(80), nullable = True , unique = False)
    password = db.Column(db.String(200), nullable = True , unique = False)
    # relation avec la table muse 
    muse_id = db.Column(db.Integer , db.ForeignKey("muse.id") , nullable = True) 
    # relation avec la table role 
    role_id = db.Column(db.Integer , db.ForeignKey("role.id") , nullable = True) 
    

#
# insert defaut user 

    
   
    

# class permission
class Permission(db.Model):
    __tablename__ = 'permission'

    id = db.Column(db.Integer , primary_key = True)
    lib_permission = db.Column(db.String(40), nullable  =True , unique = False)

    



# table role
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer , primary_key = True)
    lib_role = db.Column(db.String(40), nullable  =True , unique = False)

    # relation avec la table user 
    user = db.relationship("User", backref = 'role', lazy = True) 

#
#
# role par defaut
#

#
#
# roles 
# @app.route('/')
# def role():
#     role = Role.query.all()
#     roles = db.session.query(Role.lib_role).all()

    # return render_template('role.html' , role = role , roles = roles) 
@app.route('/', methods = ['POST','GET'])
@app.route('/login', methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        pwd   = request.form.get('pwd') 

        use = User.query.filter_by(email = email , password = pwd).first()

        if use :
            session['session'] = True 
            session['id'] = use.id
            session['name'] = use.name
            session['role'] = use.role_id
            session['muse'] = use.muse_id

            return redirect('/home')
            
        else:
            flash("mot de passe erroner !!!")
    return render_template('back-end/auth-login.html')


#
#
# dashbord
#
#
@app.route('/home')
def home():
    if 'session' in session:
        return render_template('back-end/index.html')
    else :
        return redirect('/login')
    
#
#
# deconnexion
@app.route('/deco')
def deco():
    session.clear()
    return redirect('/login')


## creation des muse 
@app.route('/muse', methods =['POST','GET'])
def muse():
    if 'session' in session:
        if request.method == 'POST':
            nomM = request.form.get('nomM')
            province = request.form.get('province')

            existe_muse = Muse.query.filter_by(nom = nomM).first()

            if existe_muse:
                flash(f"le {nomM} existe deja dans le systeme ") 
            else:
                mu = Muse(nom = nomM , province = province) 
                db.session.add(mu) 
                db.session.commit()
                flash("information enregistre ")
                return redirect('/muse')
            
        return render_template('back-end/forms-validation.html')
    else:
        return redirect('/login')
    
##
#
# ajout des utilisateurs du systeme par muse

@app.route('/adduser', methods=['POST','GET'])
def adduser():
    if 'session' in session :
    #post 
        if request.method == 'POST':
            user = request.form['user'] 
            email = request.form['email'] 
        
            fonction = 'sous-admin' 
        
        
            password = 12345
            if session['role'] == 2:
                roles = request.form['role']
                muse    = request.form['muse']
            else :
                role  = 2
                muse  = request.form['muse']


        #verification du doublon sous-admin
        # 
        #
            sous = User.query.filter(and_(User.role_id == 2 , User.muse_id == muse)).first()

        # mail existe
            mail =User.query.filter_by(email = email).first()

            if  mail:
                flash("l'email existe deja dans le system !!! ")
            elif session['role'] == 1 :
                if sous:
                    flash("le sous-admin existe deja dans le muse !!!")  
                else :
                    send_info = User(name = user , email = email , password = password , muse_id = muse , role_id = role)
                    db.session.add(send_info)
                    db.session.commit()
                    flash("Information enregistre ")
                    return redirect('/adduser')   
            #
            # 
            # sous admin 
            #    
            elif session['role'] == 2 :
                send_info = User(name = user , email = email , password = password , muse_id = muse , role_id = roles)
                db.session.add(send_info)
                db.session.commit()
                flash("Information enregistre ")
                return redirect('/adduser') 
            else:
            
                flash("Null requete ")
                return redirect('/adduser')        
        


    # appel a la table muses
        mus = Muse.query.all()

    # appel a la table role 
        roles_call = Role.query.filter(Role.id.notin_([1,2])).all()

        return render_template('back-end/forms-users.html' , muse = mus , roles = roles_call )
    
    else:
        return redirect('/login')

#
#
##
# liste des utilisateurs code sous admin
@app.route('/lstU', methods=['POST','GET'])
def lstU():
    #liste des utilisteurs du systemes

    lst = User.query.all()

    # jointure 
    jointure = db.session.query(User).join(Role).join(Muse).add_columns(User.id , User.name,User.email , Role.lib_role,Muse.nom,Muse.province).all()
    
  

    return render_template('back-end/export-table.html' , lst =lst , jointure = jointure )



if __name__ == '__main__':
    app.run(debug=False) 