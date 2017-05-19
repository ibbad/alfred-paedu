"""
Module containing generic functions for Jinja2 Template.
"""

from flask import render_template, current_app, abort, request
from app.webapp import webapp, webapp_logger
from app.models import User, Comment, Tag


@webapp.route('/')
@webapp.route('/index')
def index():
    return render_template('index.html')


@webapp.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'

"""
Helper functions for JINJA2 templates. These functions are used to performs
lightweight functionality inside JINJA2 template without providing full
object to the template.
"""


@webapp.add_app_template_global
def get_fullname_from_id(user_id):
    """
    Returns the first name and last name of the subscriber whose id is provided.
    :param user_id: ID of the subscriber whose first and last name is required.
    :return (firstname, lastname): String tuple
    """
    user = User.objects(id=user_id).first()
    if user is not None:
        webapp_logger.debug('Returning subscriber %d name' % user.id)
        return user.first_name, user.last_name
    else:
        webapp_logger.warning('Subscriber %d not found in database.' % user_id)
        return ''


@webapp.add_app_template_global
def get_username_from_id(user_id):
    """
    Returns the username of the subscriber whose id is provided.
    :param user_id: ID of the subscriber whose first and last name is required.
    :return username: String.
    """
    user = User.objects(id=user_id).first()
    if user_id is not None:
        webapp_logger.debug('Returning user %d username to jinja2 '
                            'template.' % user.id)
        return user.username
    else:
        webapp_logger.warning('User %d not found in database.' % user_id)
        return ''


@webapp.add_app_template_global
def get_post_comment_count(post_id):
    """
    Returns the count for comments on given post.
    :param user_id: ID of the subscriber whose first and last name is required.
    :return username: String.
    """
    return Comment.objects(c_type=current_app.config["COMMENT_TYPE"][
        "POST"], post_id=post_id).count()

@webapp.add_app_template_global
def get_activity_comment_count(activity_id):
    """
    Returns the count for comments on given activity.
    :param user_id: ID of the subscriber whose first and last name is required.
    :return username: String.
    """
    return Comment.objects(c_type=current_app.config["COMMENT_TYPE"][
        "ACTIVITY"], post_id=activity_id).count()


@webapp.add_app_template_global
def get_tag_text(tag_id):
    """
    """
    return Tag.objects(id=tag_id).first().text or ''


@webapp.add_app_template_global
def get_tag_text_list(tag_id_list):
    """
    Returns the text of tag from the database.
    :param tag_id: list of tag_ids.
    :return list of tags (text): String.
    """
    return ','.join([Tag.objects(id=i).first().text
                     for i in tag_id_list])


def _add_user_associations():
    from app.models import User, Address
    # Add alfred
    user = User(
        username='alfred',
        email='alfred@paedu.com',
        first_name='Alfred',
        last_name='PAEdu',
        confirmed=True,
        phone='+358-40-555-5555'
    )

    address = Address(
        street='Team Finland',
        city='Helsinki',
        postal_code='00140',
        country='Finland'
    )
    user.address = address
    user.confirmed = True
    user.set_password('password')
    user.save()

    # Add alfred's parents
    dad = User(
        username='alfred_senior',
        email='alfred.sr@paedu.com',
        first_name='Alfred',
        last_name='Senior',
        confirmed=True,
        phone='+358-40-555-5556',
        role=2
    )

    address = Address(
        street='Team Finland',
        city='Helsinki',
        postal_code='00140',
        country='Finland'
    )
    dad.address = address
    dad.confirmed = True
    dad.set_password('password')
    dad.save()

    mom = User(
        username='alberta',
        email='mrs-alfred@paedu.com',
        first_name='Alberta',
        last_name='Alfred',
        confirmed=True,
        phone='+358-40-555-5557',
        role=2
    )

    address = Address(
        street='Team Finland',
        city='Helsinki',
        postal_code='00140',
        country='Finland'
    )
    mom.address = address
    mom.confirmed = True
    mom.set_password('password')
    mom.save()

    user.parents = [mom.id, dad.id]
    user.save()

    # Add fake users
    User.generate_fake(5)

    # Add teacher
    teacher = User(
        username='john',
        email='john@paedu.com',
        first_name='John',
        last_name='Doe',
        confirmed=True,
        phone='+358-40-400-5000',
        role=3
    )

    address = Address(
        street='Team Finland',
        city='Helsinki',
        postal_code='00140',
        country='Finland'
    )
    teacher.address = address
    teacher.confirmed = True
    teacher.set_password('password')
    teacher.save()
    user.teachers = [teacher.id]
    user.save()

    # Add friendships
    uid = User.objects.values_list('id')
    for user in User.objects.all():
        for i in uid:
            if user.id != i:
                user.friends.append(i)
                user.save()


def _generate_dummy_data():
    from app.models import Tag, Activity, Diary, Post, Comment
    Tag.generate_fake(50)
    Post.generate_fake(50)
    Diary.generate_fake(10)
    Activity.generate_fake(10)
    Comment.generate_fake(100)


def _load_activity_data():
    from app.models import Activity, Tag
    import random
    from datetime import datetime
    u = User.objects(username='alfred').first()
    users = User.objects(username__ne='alfred').values_list('id')
    # Activity 1
    a = Activity(
        title='Picnic to Suomenlinna',
        description='Day picnic to Suomenlinna. We will leave at 10 am in '
                    'the morning and come back at 7 pm in the evening.',
        activity_time=datetime.strptime('06/11/2017', "%m/%d/%Y"),
        tags=[Tag(text='suomenlinna').save().id,
              Tag(text='picnic').save().id,
              Tag(text='summer').save().id],
        author_id=u.id
    ).save()
    a.comments = [Comment(body='Who would like to go for shopping with me?',
                          c_type=2,
                          post_id=a.id,
                          commenter_id=u.id).save().id,
                  Comment(body='What are allergies to avoid??',
                          c_type=2,
                          post_id=a.id,
                          commenter_id=u.id).save().id,
                  Comment(body='Cool! What should we bring for food?',
                          c_type=2,
                          post_id=a.id,
                          commenter_id=random.choice(users)).save().id,
                  Comment(body='I can bring some food and drinks',
                          c_type=2,
                          post_id=a.id,
                          commenter_id=random.choice(users)).save().id,
                  ]
    a.going =users[1:3]
    a.interested =users[3:]
    a.save()
    # Activity 2
    a = Activity(
        title='Exploring Medieval History',
        description='I am doing a self learning project on exploring '
                    'medieval history. Who would like to join me on the '
                    'quest?',
        activity_time=datetime.strptime('07/01/2017', "%m/%d/%Y"),
        tags=[Tag(text='history').save().id,
              Tag(text='learning').save().id,
              Tag(text='fun').save().id],
        author_id=u.id
    ).save()
    a.comments = [Comment(body='Sounds fun',
                          c_type=2,
                          post_id=a.id,
                          commenter_id=random.choice(users)).save().id,
                  Comment(body='Where is this going to happen?',
                          c_type=2,
                          post_id=a.id,
                          commenter_id=random.choice(users)).save().id,
                  Comment(body='I would love to join. Can I?',
                          c_type=2,
                          post_id=a.id,
                          commenter_id=random.choice(users)).save().id,
                  Comment(body='What are the events you are going to look '
                               'into?',
                          c_type=2,
                          post_id=a.id,
                          commenter_id=random.choice(users)).save().id,
                  ]
    a.going = users[1:2]
    a.interested = users[2:]
    a.save()

    # Activity 3
    a = Activity(
        title='Birthday party',
        description="Our teacher's birthday is coming up and we plan to bake "
                    "a cake for her, who is interested to join?",
        activity_time=datetime.strptime('06/30/2017', "%m/%d/%Y"),
        tags=[Tag(text='birthday').save().id,
              Tag(text='BestTeacherEver').save().id,
              Tag(text='celebration').save().id],
        author_id=u.id
    ).save()
    a.comments = [Comment(body='Hey, where are we celebrating?',
                          c_type=2,
                          post_id=a.id,
                          commenter_id=random.choice(users)).save().id,
                  Comment(body='What kind of cake are you guys planning to '
                               'make? I have a nice recipe for blueberry '
                               'cake.',
                          c_type=2,
                          post_id=a.id,
                          commenter_id=random.choice(users)).save().id,
                  Comment(body='I would love to join. Always wanted to learn '
                               'cake baking.',
                          c_type=2,
                          post_id=a.id,
                          commenter_id=random.choice(users)).save().id,
                  ]
    a.going = users[2:4]
    a.interested = [i for i in users if i not in a.going]
    a.save()

    # Activity 4
    a = Activity(
        title='Movie Night: Fun Night',
        description="I have some movie tickets, who would like to join me in "
                    "on the new  STAR WARS.",
        activity_time=datetime.strptime('05/20/2017', "%m/%d/%Y"),
        tags=[Tag(text='StarWards').save().id,
              Tag(text='MovieNight').save().id,
              Tag(text='Freedom').save().id],
        author_id=u.id
    ).save()
    a.comments = [Comment(body='Wanna grab a bite before going for movie?',
                          c_type=2,
                          post_id=a.id,
                          commenter_id=random.choice(users)).save().id,
                  Comment(body="I will mark in my calendar",
                          c_type=2,
                          post_id=a.id,
                          commenter_id=random.choice(users)).save().id,
                  Comment(body='I heard they are screening it in 3D?',
                          c_type=2,
                          post_id=a.id,
                          commenter_id=random.choice(users)).save().id,
                  ]
    a.going = users[1:4]
    a.interested = users[4:]
    a.save()

    # Activity 5
    a = Activity(
        title='Football',
        description="Playing football this weekend, "
                    "who wants to join?",
        activity_time=datetime.strptime('05/20/2017', "%m/%d/%Y"),
        tags=[Tag(text='boring').save().id,
              Tag(text='footbal').save().id,
              Tag(text='weekendsports').save().id],
        author_id=u.id
    ).save()
    a.comments = [Comment(body='Anyone interested in badminton?',
                          c_type=2,
                          post_id=a.id,
                          commenter_id=random.choice(users)).save().id,
                  Comment(body="Be there, got to get my spikes before that?",
                          c_type=2,
                          post_id=a.id,
                          commenter_id=random.choice(users)).save().id,
                  Comment(body='Hurrah, summer time, football time',
                          c_type=2,
                          post_id=a.id,
                          commenter_id=random.choice(users)).save().id,
                  ]
    a.going = users[1:3]
    a.interested = users[3:]
    a.save()


def _load_post_Data():
    from app.models import Post, Tag
    import random
    u = User.objects(username='alfred').first()
    users = User.objects(username__ne='alfred').values_list('id')
    # Post 1
    p = Post(
        body='I missed the history class today, what did we cover?',
        tags=[Tag(text='lecture').save().id,
              Tag(text='homework').save().id],
        author_id=u.id
    ).save()
    p.comments = [Comment(body='Hey, heard you were sick, '
                               'are you feeling better?',
                          c_type=1,
                          post_id=p.id,
                          commenter_id=random.choice(users)).save().id,
                  Comment(body="We were talking about the Cold War, "
                               "I'll share the extra material",
                          c_type=1,
                          post_id=p.id,
                          commenter_id=random.choice(users)).save().id,
                  Comment(body='Yeah, we have to read the next chapter for '
                               'the next class as well',
                          c_type=1,
                          post_id=p.id,
                          commenter_id=random.choice(users)).save().id,]
    p.save()

    # Post 2
    p = Post(
        body="HELP! I'm stuck on question 5 on our Math assignment",
        tags=[Tag(text='math').save().id,
              Tag(text='bored').save().id],
        author_id=u.id
    ).save()
    p.comments = [Comment(body="Oh that, I'm stuck on that as well",
                          c_type=1,
                          post_id=p.id,
                          commenter_id=random.choice(users)).save().id,
                  Comment(body="I can help you on that.",
                          c_type=1,
                          post_id=p.id,
                          commenter_id=random.choice(users)).save().id,
                  Comment(body='For that question, the answer is (x)',
                          c_type=1,
                          post_id=p.id,
                          commenter_id=random.choice(users)).save().id,
                  Comment(body='Really? I got a different answer, '
                               'how did you solve it?',
                          c_type=1,
                          post_id=p.id,
                          commenter_id=u.id).save().id]
    p.save()

    # Post 3
    p = Post(
        body="I found our book for Finnish class very difficult. "
             "How do you feel about it? ",
        tags=[Tag(text='finnish').save().id,
              Tag(text='SuperDifficult').save().id],
        author_id=u.id
    ).save()
    p.comments = [Comment(body="Why do you feel it is difficult? "
                               "I found it very boring and that's why "
                               "it is difficult to continue reading. ",
                          c_type=1,
                          post_id=p.id,
                          commenter_id=random.choice(users)).save().id]
    p.save()


def _load_suggestion_Data():
    from app.models import Suggestion
    import random
    # Suggestion 1
    s = Suggestion(
        query='Do I have any schoolwork for today?',
        responses=["Yes, You have the following tasks that need your "
                   "attention.<ol> <li>Math- Finish by Friday</li>"
                   "<li>Geography- Fast approaching</li></ol>",
                   "Currently, You don't have any homework tasks.",
                   "The list homeworks and their status"
                   "<ol><li>Math Test- Studied</li>"
                   "<li>History project- Ongoing</li></ol>"]
    ).save()
    # Suggestion 2
    s = Suggestion(
        query="Can you tell me some information to read about the Winter's "
               "war??",
        responses=["These are some good books(recommendations)."
                   "<ol> <li>A Frozen Hell: The Russo-Finnish Winter War of "
                   "1939-1940 by William R. Trotter(Englanti) </li>"
                   "<li>Talvisodan aika by Eeva Kilpi(Suomi)</li></ol",

                   "The following people have made a presentation about the "
                   "Winter's War. ",
                   "<ol><li>Pekka Suomalainen</li>"
                   "<li> Andrii Stan </li>"
                   "<li>Tiina Carlson </li></ol>"
                   "Do you want to ask them for their material?",

                   "Here are some information that I found from Wikipedia "
                   "and Youtube",
                   "<ol><li>Winter's War(Englanti)</li>"
                   "<li>BBC Documentary(2014)-Winter's War</li></ol>"]
    ).save()

    # Suggestion 3
    s = Suggestion(
        query=" Is any one in my school interested in Football?",
        responses=["There are 45 people interested in football from your school. "
                   "<ol> <li>K10-13 - 20</li>"
                   "<li>K15-17- 25</il></ol",

                   "Here are some football training sessions in your school.",
                   "<ol><li>K10-13- 3:00 PM</li>"
                   "<li> K15-17- 4:00 PM</li></ol>",

                   "No, I could not find any relevant information. But, "
                   "Here are some suggestion from the parents for Football. ",
                   "<ol><li> Gaelic Football Club</li>"
                   "<li>Soccer Kumpula</li></ol>"]
    ).save()

    # Suggestion 4
    s = Suggestion(
        query="Tell me about Parkour?",
        responses=[
            "Here is some information Wikipedia. <Parkour- Wikipedia",

            "People from your school are interested in Parkour. Do you want "
            "to start a group activity ?",

            "No relevant information was found. "]
    ).save()

    # Suggestion 5
    s = Suggestion(
        query="Tell me more about Mozart ",
        responses=[
            "Wolfgand Amadeus Mozart (1756-1791), was one of the famouse "
            "composers of the Classical Era. More about Mozart's biography "
            "<a href='http://www.allmusic.com/artist/wolfgang-amadeus-mozart-mn0000026350/biography'>link</a>",

           "Famous compositions by Mozart",
           "<ol><li>Symphony No. 40</li>"
           "<li>Eine Kleine Nachtmusik</li>"
           "<li>Don Giovanni</li></ol>",

            "Are you interested in learning musical instrument as well?",
           "<ol><li>World Music School Helsinki</li>"
           "<li>Eine Kleine Nachtmusik</li>"
           "<li>Helsinki Conservatory School of Music</li></ol>"]
    ).save()

    # Suggestion 6
    s = Suggestion(
        query="What is the Renaissance Art Movement?",
        responses=[
            "Renaissance Art Movement was from 1400-1600 and has 12 "
            "characteristics <a "
            "href='http://www.identifythisart.com/art-movements-styles/pre"
            "-modern-art/renaissance-art-movement/'>link</a>",

            "Examples of Renaissance artists and their work",
            "<ol><li>Leonardo da Vinci - The Last Supper, Mona Lisa</li>"
            "<li>Raphael - The School of Athens</li>"
            "<li>Michelangelo - David</li>"
            "<li>Giovanni Bellini - The Feast of the Gods</li></ol>",

            "Here are a few art museums in Helsinki where there might be relevant exhibitions",
            "<ol><li>National Museum of Finland</li>"
            "<li>Helsinki Art Museum HAM</li>"
            "<li>Anteneum Art Museum</li></ol>"]
    ).save()

    # Suggestion 7
    s = Suggestion(
        query="What are some activites organized in my city this month?",
        responses=[
            "Worry about the weather for your plan? Check them out "
            "<a href='http://ilmatieteenlaitos.fi'>here</a>",

            "These events might interest you",
            "<ol><li>Adventure in Suomenlinna: June 6th with free entrance to 6 museums on Suomenlinna</li>"
            "<li>Living Science for Visitors of All Ages at Natural History Museum, Kaisaniemi Botanic Garden, Kumpula Botanic Garden</li>"
            "<li> Exhibitions at Finnish Science Centre Heureka</li></ol>",

            "You can find more information about activities in your city at these websites:",
            "<ol><li><a href='https://www.helsinkicard.com'>link1</a></li>"
            "<li><a href='http://www.visithelsinki.fi'>link1</a></li></ol>"]
    ).save()

    # Suggestion 8
    s = Suggestion(
        query="Where is Venezuela?",
        responses=[
            "Venezuela located on the northern coast of South America. Find "
            "more interesting facts <a "
            "href='http://www.sciencekids.co.nz/sciencefacts/countries"
            "/venezuela.html'>here</a>",

            "Places to visit in Venezuela",
            "<ol><li><a href='https://www.thecrazytourist.com/15-best-places"
            "-visit-venezuela/'>link1</a></li>"
            "<li><a href='http://www.touropia.com/tourist-attractions-in"
            "-venezuela/'>link2</a></li>"
            "<li><a href='http://www.planetware.com/tourist-attractions"
            "/venezuela-ven.htm'>link3</a></li></ol>",

            "There are 12 people on Alfred who has visited or written paper about Venezuela, wanna talk to them?"]
    ).save()

    # Suggestion 9
    s = Suggestion(
        query="How do I lose weight?",
        responses=[
            "Worried about your weight? Check your BMI to see if you are in "
            "a healthy weight range "
            "<a href='https://www.nhlbi.nih.gov/health/educational/lose_wt/BMI"
            "/bmicalc.htm'>link</a>. If you are still in doubt, please "
            "consult with your school doctors before going on a diet to "
            "ensure you are healthy or your plan is safe for you. ",

            "Lose weight safely is a combination of eating right and "
            "moderate exercise. Look at these before making your plan "
            "<a href='http://kidshealth.org/en/teens/managing-weight-center"
            "/losing-weight/?WT.ac=en-t-weight-center-i#catdieting'>link</a"
            "></ol>",

            "Other disorders related to health:",
            "<ol><li><a href='http://www.who.int/mediacentre/factsheets"
            "/fs311/en/'>Obestity</a></li>"
            "<li>"
            "<a href='http://www.mielenterveysseura.fi/en/home/mental-health"
            "/mental-disorders/eating-disorders'>Eating "
            "disorders</a></li></ol>"]
    ).save()






































