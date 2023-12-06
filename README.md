# DTF_against_inflation_for_Chinese

This is the group assignment of Digital Tools for Finance from University of Zurich

Collaboration with:


## Research Question:
What type of assets can provide effective protection against inflation for Chinese people?


## Guide To Building The Visualization Tool
### Prerequisites
Before you begin, ensure your system meets the following requirements:
#### Environment Setup
1. **Python:** version 3.9 or higher
2. **Jupyter Notebook:** For interactive code execution.
3. **Docker:** To run the tool in a containerized environment.

**Version Check** <br>
To check if these tools are installed and their versions, use the following commands in your command line interface:
```bash
python --version
jupyter notebook --version
docker --version
```

**Installation Guide**
If you need to install or update these tools, please refer to the following links:
- [For python compiler](https://www.python.org/downloads/)
- [For Jupyter Notebook](https://jupyter.org/install)
- [For Docker](https://www.docker.com/get-started/)

### Docker Container Setup
#### Pulling the Docker Image
To use our Dockerized Visualization Tool, start by pulling the image from the Docker Hub. In your command line interface, run
```bash
docker pull darleneqing/my_bokeh
```

#### Running the Docker Container
Then navigate to the working directory to the file that saves your cloned git repository
```bash
cd <Disk:\your_git_clone_file_path>  #(Replace the <Disk:\your_git_clone_file_path> of your choice)
```

Then, start the Docker container:
```bash
docker run -p 8888:8888 my_bokeh
```

Now your Jupyter notebook server should start running, you can access it at: 'http://localhost:8888'

### Exploring the Visualization Tool
Open the file Hedge_Against_inflation_Tool.ipynb in Jupyter Notebook. This notebook is your main interface for using our visualization tool. Follow the embedded comments and instructions to start to know more about our research. Enjoy!

### Troubleshooting Docker Image Issues
**Solution One**
1. Navigate to the directory of *DTF_against_inflation_for_Chinese*, run in command line interface:
```bash
pip install -r requirements.txt
```
2. Start the jupyter notebook under the same directory
```bash
jupyter notebook --port=8888
```
3. Open the file 'Hedge_Against_inflation_Tool.ipynb' in jupyter botebook.

**Solution Two**
*In case your jupyter notebook is still not working* <br>
1. Open the DTF_against_inflation_for_Chinese folder in your preferred Python IDE.
2. Install necessary dependencies. Open a terminal, run
```bash
pip install -r requirements.txt
```
3. In terminal again, run
```bash
bokeh serve --show backup_vs_tool.py
```


