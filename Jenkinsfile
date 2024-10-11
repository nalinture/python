pipeline {
    agent any 

    stages {
        stage('Build') {
            steps {
                echo 'Building the application...'
                sh 'npm install'  // Install dependencies
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                sh 'npm test'  // Run tests
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying the application...'
                sh 'echo "Deploying to production..."'  // Deploy command
            }
        }
    }
}
