
    
def is_it_running():
    for process in psutil.process_iter(attrs=['pid','name']):
        if 'msedge' in process.name():
            print(process.name())
            process.kill()


def kill_open_browser():
    for process in psutil.process_iter(attrs=['pid','name']):
        if 'msedge' in process.name():
            process.kill()

def is_it_running():
    print('is it runnin')
    processes = list((psutil.process_iter(attrs=['pid','name'])))
    #print(len(processes))
    for process in processes:
        #print(len(processes))
        #cpu_usage = process.cpu_percent(0.5)
        #print(process.name())
        try:
            if 'msedge' in process.name():
                print('found msedge')
                cpu_usage = process.cpu_percent(0.5)
                if cpu_usage >0:
                    print('found process')
                    return True
            #print('in for loop')
        except Exception as error:
            print(error)
            print('could not found process')
            return False
            
    print('could not found process')
    return False

def plot_is_shown():
    print('plt shown')
    time.sleep(3)
    browser_is_running = True
    while browser_is_running:
        browser_is_running = is_it_running()
    print('you closed msedge')
    keyboard.press_and_release('ctrl+c')
    print('terminated!')
    
   
def images2gif(input_dir_path,output_filename,frame_duration=0.5):
    image_filenames = [f for f in os.listdir(input_dir_path) if os.path.isfile(os.path.join(input_dir_path,f))]
    #print(image_filenames)
    images = []
    for filename in image_filenames:
        filename = os.path.join(input_dir_path,filename)
        img = Image.open(filename)
        images.append(img)
    imageio.mimsave(output_filename,images,duration=frame_duration)
