from setuptools import setup, find_packages

setup(
    name='MeetingAssistant',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'PySimpleGUI==4.60.5',
        'llama-cpp-python==0.1.0',  # Adjust version if needed
        'faiss-cpu==1.7.4',  # or 'faiss-gpu'
        'python-telegram-bot==20.7',
    ],
    author='Samruddhi Tiwari',  
    author_email='samruddhitiwari003@gmail.com',  
    description='A conversational meeting assistant',
    long_description=open('README.md').read(),  # Fixed syntax error here
    long_description_content_type='text/markdown',
    url='https://github.com/samruddhitiwari/MeetingAssistant',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': [
            'meeting-assistant=meeting_assistant.app:main',  # Assuming your main entry point is in `app.py`
        ],
    },
    python_requires=">=3.8",  # Adjust depending on your Python version
)
