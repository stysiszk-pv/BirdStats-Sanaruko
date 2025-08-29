# Function to set background color for cancelled status
def bg_cancelled(val):
    color = '#FFCCCC' if val=='Cancelled' else 'white'
    return f'background-color: {color}'