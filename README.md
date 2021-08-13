# falcon_app
provision and deployment using aws, vault, terraform, ansible, jenkins, docker, python app
* We will build two servers (AWS EC2) with Terraform (Infra as code) and then configure them with the requirements needed for the project. Box one will be Jenkins and Box two will be configured for Docker and able to listen on port 8000 for our python app using the Falcon framework.
1:  Set Up AWS User and Access

  Click 'Users' and create a new user. Call this user what you'd like and provide "Programmatic Access".
  Create a group for this user and provide administrator access.
  Click through the next two screens and get to the Create User screen. Click "Create User" and make sure you keep your security credentials safe as well as handy. You can only view these one time from the aws console. IF you are careful, you can download the csv as prompted.

  Now that we have our user and access keys, lets pop over to a terminal/shell and configure our aws account and aws-vault.

    In your terminal:

    Make sure you have the aws-cli

    pip3 install awscli --upgrade --user

    configure aws and add your Access and secret keys when prompted

    aws configure

    Now lets setup aws-vault with a username and add your access keys as prompted.

    aws-vault add devops_01

    now lets exec into that aws-vault:

    aws-vault exec devops_01

    Awesome! Now we are ready to start working from our machine and creating resources in the cloud!
 
 2: Creating the environment in Terraform
   
   Before we begin the terraform steps, let's create a key pair that we can use with our servers.

    In the aws console, navigate to Services > EC2. In the left menu panel find and click "key pairs". Follow the click through prompt to generate your key pair. Note: use ppk for putty and pem for openssh. Download that key and move it somewhere handy that makes sense (i. e. ~/.ssh).
    1.) If you haven't already, head over to Terraform's docs for installation, or use a package manager.

    2.) Check in your terminal if you have terraform installed correctly:

    terraform version
    Terraform v0.12.20

    3.) Lets create the directories we need for the terraform portion of this project (NOTE: I am using the fish shell, which is not required but easy to use. So I am bundling my command separated by "; and"):

    mkdir projects; and cd projects; and mkdir devops_01; and cd devops_01; and mkdir terraform; and cd terraform; and touch main.tf

    4.) Note that the above gives away that we will be building our jenkins server first. Let's open that main.tf file that we created in the last step and add the following (in your editor of choice, I use VS Code):

    provider "aws" {
    region = "us-east-1"
    }

    We are choosing the terraform provider "aws" and declaring the region we will be using. In my case, the free tier region that I will use is "us-east-1" on the east coast.

    Feel free to reference the AWS provider documentation at any time to better understand what fields you may want to use. In our case in standing up a jenkins server instance, we will want to create an EC2 instance with aws_instance. We will also need to add the ami (amazon machine image). In our case we will choose an Ubuntu Server image from the EC2 options. We will also want an instance_type of t2.micro. THIS IS FOR THE FREE TIER. If you go above the t2.micro, you will be charged!

    Now, let's add that key pair we created earlier for added security.

    I am also going to throw in a tag for "Name" and create a variable to be entered when we run it. As tempted as I am to go into detail, I would prefer not to turn this into a full terraform tutorial and stick to the task at hand.

    Our code should now look like this:

    ~/projects/devops_01/terraform/main.tf

    provider "aws" {
        region = "us-east-1"
    }

    variable "name" {
        description = "Name the instance on deploy"
    }

    resource "aws_instance" "devops_01" {
        ami = "ami-04b9e92b5572fa0d1"
        instance_type = "t2.micro"
        key_name = "devops_01"

        tags = {
            Name = "${var.name}"
        }
    }

    Awesome. Now from the directory that main.tf is in, lets run:

    terraform init
    if you get an auth error here, remember to aws-vault exec username

    This will grab the requirements for our aws provider.

    Fyi - you can add a gitignore file based on this reference to keep large terraform packages out.

    now, to verify that we have set this up correctly, let's run a plan! This will show us everything that we are about to change on our aws account with terraform. We can catch mistakes if there are any, without ever doing anything officially to our environment.

    terrform plan

    you should see the plan now, just take a glance and check for things specifically like instance_type.

    If all is well, let's do a

    terraform apply

    Confirm and check your aws console EC2 dashboard to watch your box spin up.

    You did it! Now on your own, spin up a container called "web". hint, use the same terraform file!
    If you are feeling juicy, ssh into one or both of your EC2 instances.

    ssh -i ~/.ssh/keyName ubuntu@public_ip_address
    One thing that we will need to configure before moving on, is the Security Groups, AWS's firewall functionality to tell our instances which connections to allow inbound and outbound.

    In your EC2 dashboard on the Instances page, click on your jenkins instance. Below you will see that is has been assigned your default security group for you VPC (virtual private network). If you click on "default" it will take you to the security group screen (or this is in the left menu).

    From here, select "Create Security Group" and call it "jenkins-server".

    In this case, but really not ever the real case, we are going to allow our IP ONLY to speak to jenkins. This would usually be done over a companies VPN. Also, not that your IP could change...so if you can't ssh into your box eventually, check the SG.

    for "inbound rules" select, "Add Rule" and select "all traffic". Then from the next drop down, pick "My IP". Outbound rules can stay open (they are by default here).

    Then repeat the same process for web, except, instead of just our IP, we want to create an ssh rule for jenkins, and an http rule for the browser to hit from anywhere.







    Now that we have our SG's made, lets hop over to the instance page again and change the security groups of both to their respective groups. To do this, click on the instance you want to change, click "Action" > "Networking" > "Change Security Groups" and then apply the group to you instance.
  
  3: Configuring our servers with Ansible
    
    Now that we have our servers up and running in the cloud, lets make sure we install and run the necessary dependencies on them.

      You will need to install ansible on your machine (typically in a professional setting there will be a host for ansible, not done from locals).

      Now that ansible is installed, we will start with our Jenkins server.

      Before diving into writing the yaml's, let's open our ansible hosts file and add a couple of things there.

      Open the hosts file: /etc/ansible/hosts in your editor (I use vim but that can be confusing if you're new to this)

      Inside the hosts file, you will see comments, lets add two hosts (anywhere), one for jenkins and one for web.

      Note: Ansible has a feature for aws EC2 and can actually autodiscover your instances and you won't have to manually update. I am NOT going to use that for this walkthrough because you ought to know the hosts file. Look that feature up! It's pretty cool, just outside of the scope i'd like to go.

      /etc/ansible/hosts

      [webservers]

      ubuntu@public_web_ip ansible_ssh_private_key_file=~/.ssh/yourKeyPair

      [jenkins]

      ubuntu@public_jenkins_ip ansible_ssh_private_key_file=~/.ssh/yourKeyPair.pem

      #lots of comments below...

      Here we

      now save that file

      lets make a new directory called "ansible" under our project folder  and create a yaml file called "provision_jenkins.yml".

      cd ~/projects/devops_01; and mkdir ansible; and cd ansible; and touch provision_jenkins.yml

      So here is where we ask ourselves what do we need to do for our jenkins server to run. Let's head over to the jenkins documentation and take a look.

      We need to install java and jenkins and then run jenkins!

      Note: Yaml files are very sensitive with tabs/spaces. If your spacing is off, it will cause an error on run.
      ~/projects/devops_01/ansible/provision_jenkins.yml

      ---
      - name: Configure Jenkins Server
        hosts: jenkins
        tasks:

          - name: Install Java Requirements
            apt:
              update_cache: yes
              name: default-jdk
            become: yes

          - name: Install Jenkins
            shell: | 
              wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -
              sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
              sudo apt-get update -y
              sudo apt-get install jenkins -y

          - name: Run Jenkins
            shell: /etc/init.d/jenkins start
            become: yes

      Feel extra free to go and look up things like update_cache and become in the official ansible docs.

      Now, we can run this playbook!

      ansible-playbook provision_jenkins.yaml

      Assuming all goes well, this playbook should install those items and then start jenkins on port 8080.
      Jump over to that public IP on port 8080 and you should receive a prompt from jenkins to create your first user!

      http://IP:8080

      Follow the prompts to create your own personal user and log in. For our example we will need to install the ssh plugin.  To install navigate to Manage Jenkins > Manage Plugins > Available and search for ssh. Check that box and install it without restart.

      OK! now that you are inside your jenkins instance and have ssh installed, lets pause and start looking into the web server configuration that will host our Docker container with a very simple Falcon app.

      lets create a file in the same directory as our provision_jenkins.yml called provision_web.yml. Let's also add the EC2 public IP to the /etc/ansible/hosts file under [webservers].

      ~/projects/devops_01/ansible/provision_web.yml

      ---
      - name: Provision Web Servers
        hosts: webservers
        tasks:

          - name: Install pip3
            apt:
              update_cache: yes
              name: python3-pip
            become: yes

          - name: Install python docker sdk
            shell: |
              pip3 install docker
            become: yes

          - name: Install docker
            apt:
              name: docker.io
            become: yes

          - name: Start Docker
            shell: |
              systemctl start docker
              systemctl enable docker
            become: yes



          And there we go. Our web server is up and ready to accept jenkins ssh!
   4: Falcon App and Dockerize it!
        The falcon app is NOT the point of this so lets be quick. I'm going to create a directory called docker in ~/projects/devops_01/ and then create three files: hello.py, requirements.txt, and dockerfile.

        cd ~/projects/devops_01; and mkdir docker; and cd docker; and touch hello.py requirements.txt dockerfile

        Falcon is a lightweight python framework that we will use in tandem with gunicorn to serve it. I'm using  a variant of the falcon tutorial on their main site.

        The dependencies we need for this will go in our requirements.txt file. So let's add that now:

        falcon==2.0.0
        gunicorn==19.9.0

        Next, lets add the falcon code to our hello.py app:

        import falcon

        class HelloResource(object):
            def on_get(self, req, resp):
                resp.status = falcon.HTTP_200
                resp.body = ("Hello, World!")

        class Page2Resource(object):
            def on_get(self, req, resp):
                resp.status = falcon.HTTP_200
                resp.body = ("This is the second page!")

        app = falcon.API()

        hello = HelloResource()

        page2 = Page2Resource()

        app.add_route('/', hello)
        app.add_route('/page2', page2)

        As you can see, we have two routes that will display different text.

        now for the juice.

        Let's open that dockerfile and get started:

        We will use the base image python: 3
        RUN pip install --upgrade pip
        make our WORKDIR /hello_worldfor the image
        COPY requirements.txt from our local directory to the workdir on the image
        RUN pip3 install -r requirements.txt to install our dependencies for the application inside the image
        COPY . . to copy the remainder of our files to the workdir
        and finally, kick off the gunicorn server and bind to port 8000 with:
        CMD ["gunicorn", "-b", "0.0.0.0:8000", "hello:app"]

        FROM python:3
        RUN pip install --upgrade pip
        WORKDIR /hello_world
        COPY requirements.txt .
        RUN pip3 install -r requirements.txt
        COPY . .
        CMD ["gunicorn", "-b", "0.0.0.0:8000", "hello:app"]

        Save that file and lets log into docker from our terminal.

        sudo docker login

        now, we can run the build in the directory our dockerfile is in and tag it for our repo (account/repo_name:tag)

        sudo docker build . -t sparlor/scottyfullstack:devops_01

        Then push it to docker

        sudo docker push sparlor/scottyfullstack:devops_01

      Once that completes we should see our docker image in the repo we created.
      
   5: Jenkins ssh and run the docker image on Web

        This is the final piece!!! We are almost there.

        Log back into your Jenkins server at http://Jenkins_IP:8080

        first, we will add ssh credentials for our web box.

        In the left menu, click credentials > system > global credentials > add credentials. Set the kind to "SSH username with private Key" and fill it in.

        Note: to get your private key text
        cat ~/.ssh/devops_01.pem

        Click Manage Jenkins > Configure System

        At the ssh plugin section, let's add our web server's details. At the time of writing, mine looks like this:
        note: port 22 is the standard ssh port and the credentials are the ones we just added.
        YOU WILL NEED TO USE THE PRIVATE IP OF YOUR WEB INSTANCE.


        Save it, and lets build our job!

        Head back to the main jenkins page. Click "New Item", name it and choose "Freestyle Project".

        In the build section of your project select "Add Build Step" > "Execute shell script on remote host using ssh".  Choose the SSH site you just created in the drop down (You may see an error...ignore it).

        The command is:
        sudo docker run -dit --name hello_world -p 8000:8000 sparlor/scottyfullstack:devops_01

        Save it, and then click on your new job and and "Build Now".

        You can then checkout the output and make sure it's running ok!
        If it is successful, grab the public IP of your web instance and throw it in the browser with :8000 at the end.
