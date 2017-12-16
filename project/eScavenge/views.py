from django.shortcuts import render, redirect
from .CLI import CLI, COMMANDS
from .models import GMFactory, Team

GM = GMFactory().get_gm()


def index(request):
    user = request.session.get( 'username' )
    if user == None:
        return render(request, 'login.html' )
    else:
        if user == GM.username:
            return redirect("/gamemaker")
    return redirect("/teamPage")

def login(request):
    message = ""
    if request.method == 'POST':
        if request.POST["username"] == GM.username:
            if GM.login(request.POST['username'], request.POST['password']) is None:
                message = "Invalid password"
            else:
                request.session['username'] = request.POST["username"]
                return render(request, 'gamemaker.html')
        try:
            u = Team.objects.get(username=request.POST["username"])
        except Team.DoesNotExist:
            message = "No user named " + request.POST["username"]
        else:
            if u.login(request.POST['username'], request.POST['password']) is None:
                message = "Invalid password"
        if message == "":
            request.session['username'] = request.POST["username"]
            userpage = Team.objects.get(username=request.session.get('username'))
            teamlist = userpage.game.teams.order_by('-points')
            teamhistory = userpage.history.all()
            context = {'team': userpage, 'teamlist': teamlist, 'teamhistory': teamhistory}
            return render(request, 'teamPage.html', context)
    return render(request, 'login.html', {'message': message})


def teamPage(request):
    user = request.session.get('username')
    team = Team.objects.get( username=request.session.get( 'username' ) )
    command = ''
    output = ''
    if request.method == 'POST':
        if request.POST.get("logoutbutton"):
            del request.session['username']
            return redirect('/')
        if request.POST.get("changeteam"):
            command += 'editteam'
            if request.POST.get('changeusername'):
                command += f' name { request.POST["changeusername"]  }'
            if request.POST.get('changepassword'):
                command += f' password {request.POST["changepassword"] }'
        elif request.POST.get("quitQuestion"):
            command += f'giveup {team.username} {team.password}'
        elif request.POST.get("answerQuestion"):
            command += f' answer {request.POST.get( "commandline", None ) }'
        output = CLI(COMMANDS).command(command, user)
        if request.POST.get('changeusername'):
           request.session['username'] = request.POST["changeusername"]
    userpage = Team.objects.get(username=request.session.get('username'))
    teamlist = userpage.game.teams.order_by('-points')
    teamhistory = userpage.history.all()
    context = {'team': userpage, 'teamlist': teamlist, 'teamhistory': teamhistory, 'output': output}
    return render(request, 'teamPage.html', context)
