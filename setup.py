from setuptools import setup, find_packages

setup(
    name='MeetingAssistant',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'PySimpleGUI',
        'llama-cpp-python',
        'faiss-cpu',  # or 'faiss-gpu'
        'python-telegram-bot',
    ],
    author='Samruddhi Tiwari',  
    author_email='samruddhitiwari003@gmail.com',  
    description='A conversational meeting assistant',
    long_description_content_type='text/markdown',
    url='https://github.com/samruddhitiwari/MeetingAssistant',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
