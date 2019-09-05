pipeline {
  agent any
  stages {
    stage('Install') {
      steps {
        sh '''#!/bin/bash -xe
source /usr/local/anaconda3/bin/activate jupyterhub
python setup.py install'''
      }
    }
  }
}
