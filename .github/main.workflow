workflow "New workflow" {
  on = "push"
  resolves = ["GitHub Action for Heroku-2"]
}

action "GitHub Action for Heroku" {
  uses = "actions/heroku@6db8f1c22ddf6967566b26d07227c10e8e93844b"
  runs = "python manage.py migrate"
}

action "GitHub Action for Heroku-1" {
  uses = "actions/heroku@6db8f1c22ddf6967566b26d07227c10e8e93844b"
  needs = ["GitHub Action for Heroku"]
  runs = "python manage.py makemigration"
}

action "GitHub Action for Heroku-2" {
  uses = "actions/heroku@6db8f1c22ddf6967566b26d07227c10e8e93844b"
  needs = ["GitHub Action for Heroku-1"]
  runs = "python manage.py migrate"
}
