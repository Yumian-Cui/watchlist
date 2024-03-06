from flask import render_template, request, url_for, redirect, flash
from flask import Flask, render_template, flash, redirect, request, session
from markupsafe import escape
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message


from app import app, db, s, mail
from app.models import User, Movie, EmailConfirmationToken
from app.forms import MovieForm, SettingsForm, LoginForm, RegisterForm, ResetPasswordForm


# Routes related to movie dashboard
@app.route('/', methods=['GET', 'POST'])
# 当用户在浏览器访问这个 URL 的时候，就会触发这个视图函数（view funciton）这里的 /指的是根地址
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:  # 如果当前用户未认证
            return redirect(url_for('index'))  # 重定向到主页
    form = MovieForm()
    if form.validate_on_submit():
        title = form.title.data
        year = form.year.data
        # Add movie to database here...
        movie = Movie(title=title, year=year, user_id=current_user.id)  # 创建记录
        db.session.add(movie)  # 添加到数据库会话
        db.session.commit()  # 提交数据库会话
        flash('Item created.')  # 显示成功创建的提示
        session.modified = True
        return redirect(url_for('index'))
    movies = Movie.query.filter_by(user_id=current_user.id).all() if current_user.is_authenticated else [] # New: Only get the current user's movies
    # movies = Movie.query.all()
    return render_template('watchlist/index.html', movies=movies, form=form)

@app.route('/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    if 'username' not in session:
        flash("You were logged out due to inactivity. Please log in again.")
        return redirect(url_for('index'))
    movie = Movie.query.get_or_404(movie_id)
    form = MovieForm(obj=movie)
    if form.validate_on_submit():
        movie.title = form.title.data
        movie.year = form.year.data
        db.session.commit()
        flash('Item updated.')
        session.modified = True # reset the session timeout eachtime user performs an action
        return redirect(url_for('index'))
    return render_template('watchlist/edit.html', movie=movie, form=form) # 传入被编辑的电影记录

@app.route('/delete/<int:movie_id>', methods=['POST'])  # 限定只接受 POST 请求
@login_required  # 登录保护
def delete(movie_id):
    if 'username' not in session:
        flash("You were logged out due to inactivity. Please log in again.")
        return redirect(url_for('index'))
    movie = Movie.query.get_or_404(movie_id)  # 获取电影记录
    db.session.delete(movie)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('Item deleted.')
    session.modified = True
    return redirect(url_for('index'))  # 重定向回主页

# Routes related to authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            identifier = form.identifier.data
            password = form.password.data

            if not identifier or not password:
                flash('Invalid input.')
                return redirect(url_for('login'))
            
            # Check if identifier is a username or an email
            user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
            if user is None:
                flash('User does not exist.')
                return redirect(url_for('register'))
            
            is_email = user.email == identifier # True if the identifier = email of the retrieved user object
            if is_email and not user.email_confirmed: 
                flash('Email registered but not confirmed. A new confirmation has been sent. Please confirm it via your inbox first.')
                token = generate_confirmation_token(user.email, user.id)
                send_email_confirmation(user.email, token)
                return redirect(url_for('login'))
            
            # Validate the password
            if user.validate_password(password):
                login_user(user)  # Log in the user
                flash('Login success.')
                session['username'] = user.username # store data in session after user logs in
                return redirect(url_for('index'))  # Redirect to the home page
            
            flash('Invalid username/email or password.')  # If validation fails, display an error message
            
            return redirect(url_for('login'))  # 重定向回登录页面

    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            email = form.email.data

            user = User.query.filter_by(username=username).first()
            if user is not None:
                flash('Username already exists. Please use another one.')
                return redirect(url_for('register'))
            
            # Check if the email already exists
            user = User.query.filter_by(email=email).first()
            if user is not None:
                flash('Email already exists. Please use another one.')
                return redirect(url_for('register'))

            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            # Generate a confirmation token and send a confirmation email
            # this try except logic might be revised in the future. 
            try:
                token = generate_confirmation_token(email, user.id)
                send_email_confirmation(email, token)
                flash('Registration successful. A confirmation email has been sent to your email address.')
            except Exception as e:
                # If sending the email fails, delete the user and the token from the database
                confirm_token = EmailConfirmationToken.query.filter_by(user_id=user.id).first()
                if confirm_token:
                    db.session.delete(confirm_token)
                db.session.delete(user)
                db.session.commit()
                flash('Error sending confirmation email. Please try again.' + str(e))
                return redirect(url_for('register'))           
        
            # login_user(user)  # log in the user
            return redirect(url_for('login'))  # redirect to the main page

    return render_template('auth/register.html', form=form)

@app.route('/confirm-email/<token>')
def confirm_email(token):
    confirm_token = EmailConfirmationToken.query.filter_by(token=token).first()
    if confirm_token and not confirm_token.used:
        user = User.query.get(confirm_token.user_id)
        user.email_confirmed = True
        db.session.commit()
        confirm_token.used = True
        db.session.commit()
        # login_user(user)  # log in the user
        flash('Your email has been confirmed. You can now log in or use it for password reset.')
        return redirect(url_for('login'))
    else:
        flash('Invalid or expired confirmation token.')
    return redirect(url_for('index'))

def generate_confirmation_token(email, user_id):
    # s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = s.dumps(email, salt='email-confirm')
    
    # Associate the token with the user and store it in the database
    confirm_token = EmailConfirmationToken(user_id=user_id, token=token)
    db.session.add(confirm_token)
    db.session.commit()

    return token

def send_email_confirmation(email, token):
    """
    Send a confirmation email to the given address.

    Args:
    email (str): The recipient's email address.
    token (str): The confirmation token to be included in the email.
    """
    msg = Message('Confirm your email', sender='noreply@wl.com', recipients=[email])
    msg.body = f"""\
Hello,

You're receiving this email because you've either registered a new account with us or prompted an email confirmation link.

Please click the following link to confirm your email address: {url_for('confirm_email', token=token, _external=True)}. You will then be redirected to login.

If you did not request this email, you can safely ignore it.

Best,
Watchlist App Team
    """
    mail.send(msg)


def send_password_reset(email, token):
    msg = Message('Reset your password', sender='noreply@wl.com', recipients=[email])
    msg.body = f"""\
Hello,

You're receiving this email because you've requested a password reset.

Please click the following link to reset: {url_for('reset_password_helper', token=token, _external=True)}.

If you did not request this email, you can safely ignore it.

Best,
Watchlist App Team
    """
    mail.send(msg)  

@app.route('/reset_password/<token>', methods=["GET", "POST"])
def reset_password_helper(token):
    form = ResetPasswordForm()
    if request.method == "POST":
        if form.validate_on_submit():
            try:
                # Attempt to load the email from the token
                email = s.loads(token, salt='reset-password', max_age=3600)  # Token is valid for 1 hour
            except Exception as e:
                flash("The password reset link is invalid or has expired.")
                return redirect(url_for('reset_password'))
            user = User.query.filter_by(email=email).first()
            new_password = form.new_password.data
            confirm_password = form.confirm_password.data
            if user:
                if not user.validate_password(new_password):
                    if new_password == confirm_password:  # check if both passwords match
                        user.set_password(new_password)
                        db.session.commit()
                        flash("Your password has been reset.")
                        # login_user(user)
                        return redirect(url_for('login'))
                    else:
                        flash("Passwords do not match.")  # return an error message if passwords do not match
                else:
                    flash("Your previous password cannot be reused.")
            else:
                flash("Invalid token or email address.")
    return render_template('auth/reset_password_helper.html', form=form)


# One shouldn't need to request their username: they need to retrieve username based on email; if they remember email then they
# can log in with their unique email identifier

@app.route('/find_username', methods=['GET', 'POST'])
def find_username():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            if user.email_confirmed:
                flash('Email confirmed already. You may now log in using your email and find your username in the settings.')
                return redirect(url_for('login'))
            else:
                token = generate_confirmation_token(email, user.id)
                send_email_confirmation(email, token)
                flash('Your email is registered but not confirmed. Please confirm it via your inbox, log in with your email and find your username in the settings.')
        else:
            flash('No account found with that email.')
        return redirect(url_for('find_username'))
    return render_template('auth/find_username.html')

@app.route('/reset_password', methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            if not user.email_confirmed:
                token = generate_confirmation_token(email, user.id)
                send_email_confirmation(email, token)
                flash('Your email is registered but not confirmed. Please confirm it via your inbox now and return to this page to proceed with password reset.')
                return redirect(url_for('reset_password'))
            token = s.dumps(email, salt='reset-password')
            # ... send `token` to user's email address ...
            try:
                send_password_reset(email, token)
            except:
                flash('Error sending reset email. Please try again.')
                return redirect(url_for('reset_password'))
            flash("Please check your email for a password reset link.")
        else:
            flash("No account found with that email.")
    return render_template('auth/reset_password.html')

@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    session.pop('username', None) # remove username from session if it's there
    return redirect(url_for('index'))  # 重定向回首页

# Routes related to user profile page
#设置页面，支持修改用户的名字
#支持用户删除账户
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if 'username' not in session:
        flash("You were logged out due to inactivity. Please log in again.")
        return redirect(url_for('index'))
    
    form = SettingsForm()
    if 'confirm_delete' in request.form:
        db.session.delete(current_user)
        db.session.commit()
        logout_user()
        flash('Your account has been deleted.')
        return redirect(url_for('index'))
    if 'resend_confirmation' in request.form:
        try:
            token = generate_confirmation_token(current_user.email, current_user.id)
            send_email_confirmation(current_user.email, token)
            flash('Confirmation has been re-sent. Please check your inbox.')
        except Exception as e:
            flash('Failed to send email. Please try again later or contact support.')
        session.modified = True
        return redirect(url_for('settings'))        

    if form.validate_on_submit():

        # Map form fields to user attributes
        field_map = {
            'name': form.name.data,
            'username': form.username.data,
            'email': form.email.data
        }

        changes = []
        for field, new_value in field_map.items():
            old_value = getattr(current_user, field)
            if new_value != old_value:
                if field == 'email' and not update_email(current_user, new_value):
                    continue
                setattr(current_user, field, new_value)
                changes.append(field)

        if changes:
            db.session.commit()
            flash('Settings updated: ' + ', '.join(changes) + '.')
            session.modified = True
        return redirect(url_for('settings'))

    elif request.method == 'GET':
        form.name.data = current_user.name
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template('profile/settings.html', form=form)



# Assume you're updating your email (!= old email)
# If success in sending confirmation to the new email address, then return True; if not False.
def update_email(user, new_email):
    try:
        token = generate_confirmation_token(new_email, user.id)
        send_email_confirmation(new_email, token)
    except Exception as e:
        flash('Failed to send confirmation email. Please try again later or contact support team.')
        return False
    user.email_confirmed = False #change it to False before user confirms new email
    flash('A confirmation email has been sent to your new email address. Please confirm it promptly.')
    return True

@app.route('/reset-session', methods=['POST'])
def reset_session():
    session.permanent = True
    return {'status': 'session reset'}

@app.route('/user/<name>')
def user_page(name):
    return f'User: {escape(name)}'

@app.route('/test')
def test_url_for():
    # 下面是一些调用示例（请访问 http://localhost:5000/test 后在命令行窗口查看输出的 URL）：
    print(url_for('index'))  # 生成 hello 视图函数对应的 URL，将会输出：/
    # 注意下面两个调用是如何生成包含 URL 变量的 URL 的
    print(url_for('user_page', name='greyli'))  # 输出：/user/greyli
    print(url_for('user_page', name='peter'))  # 输出：/user/peter
    print(url_for('test_url_for'))  # 输出：/test
    # 下面这个调用传入了多余的关键字参数，它们会被作为查询字符串附加到 URL 后面。
    print(url_for('test_url_for', num=2))  # 输出：/test?num=2
    return 'Test page'

