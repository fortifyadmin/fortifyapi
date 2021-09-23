@Library('snc-jenkins-pipelines') _

pipeline {
    agent {
        label 'fortify'
    }

    environment {
        PATH="$PATH:$HOME/.local/bin"
    }

    stages {
        stage('Prepare') {
            steps {
                script {
                    sh 'pip3 install twine --user'
                    sh 'pip3 install bump2version --user'
                    sh 'pip3 install nose --user'
                }
            }
        }
        stage('Build') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'ssc-test-creds', passwordVariable: 'PYSSC_PASSWORD', usernameVariable: 'PYSSC_USERNAME')]) {
                    withCredentials([string(credentialsId: "devCiTokenEncoded", variable: "PYSSC_TOKEN")]) {
                        sh 'python3 setup.py nosetests'
                    }
                }
                sh 'python3 setup.py install --user'
            }
        }
        stage('Release') {
            when {
                branch 'master'
                not {
                    changelog '.*^Bump version: .+$'
                }
            }
            steps {
                sh "git checkout ${BRANCH_NAME}"
                sh "git reset --hard origin/${BRANCH_NAME}"
                sh 'bumpversion patch'
                sh 'python3 setup.py sdist bdist_wheel'
                withCredentials([usernamePassword(credentialsId: 'public-jenkins-pypi-stabe-user', passwordVariable: 'TWINE_PASSWORD', usernameVariable: 'TWINE_USERNAME')]) {
                    sh "twine upload dist/*"
                }
                //sh 'git log -p -2'
                sh 'git push origin ${BRANCH_NAME}'
                sh 'git push origin --tags'
            }
        }
    }
}
