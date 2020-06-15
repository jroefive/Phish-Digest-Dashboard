import pandas as pd

#Retrieve the ID number of the show that user inputs.
def get_show_date_id(date):
    track_length_combined = pd.read_csv('https://jroefive.github.io/track_length_combined')
    sd = str(date)
    # Make sure the date input is in the database
    show_date_id = track_length_combined[track_length_combined['date']==sd]['order_id'].values
    # Previous line creates a series of the same ID values, so need to reset to equal just the first value.
    show_date_id = show_date_id[0]
    return show_date_id

# Check to see how many songs are in each set of the show and if a set has a song then include that as an option to view
def reset_sets_list(show_date):
    sets = []
    show_id  = get_show_date_id(show_date)
    track_length_combined = pd.read_csv('https://jroefive.github.io/track_length_combined')
    show_only = track_length_combined[(track_length_combined['order_id']==show_id)]
    show_only = show_only.sort_values(by='position')
    show_songs_s1 = show_only[show_only['set']=='1']['title'].values
    if len(show_songs_s1)>0:
        sets.append('Set 1')
    show_songs_s2 = show_only[show_only['set']=='2']['title'].values
    if len(show_songs_s2)>0:
        sets.append('Set 2')
    show_songs_s3 = show_only[show_only['set']=='3']['title'].values
    if len(show_songs_s3)>0:
        sets.append('Set 3')
    show_songs_e = show_only[(show_only['set']=='E') | (show_only['set']=='E2')]['title'].values
    if len(show_songs_e)>0:
        sets.append('Encore')
    return sets

#Export data from dataframe as songlist for set and dicts for graphing go.Box
def get_data(set, type, date, shows_to_highlight):
    #Pull in every track in every show and the duration of the song, need a second version of this because the set placement df doesn't have a set column
    tracks_df = pd.read_csv('https://jroefive.github.io/track_length_combined')
    #Set the graphing df based on graph type input
    if type == 'Song Duration':
        tracks_graph = pd.read_csv('https://jroefive.github.io/track_length_combined')
    elif type == 'Set Placement':
        tracks_graph = pd.read_csv('https://jroefive.github.io/set_placement_plot')

    #Get show_id and all the songs played in the show then sort by position in show for graph display
    show_id = get_show_date_id(date)
    show_songs = tracks_df[tracks_df['order_id'] == show_id]
    show_songs = show_songs.sort_values(by=['position'])

    #Slice off just the songs that were played in the chosen set
    if set == 'Set 1':
        set_songs = show_songs[show_songs['set'] == '1']['title'].values
    elif set == 'Set 2':
        set_songs = show_songs[show_songs['set'] == '2']['title'].values
    elif set == 'Set 3':
        set_songs = show_songs[show_songs['set'] == '3']['title'].values
    elif set == 'Encore':
        set_songs = show_songs[(show_songs['set'] == 'E') | (show_songs['set'] == 'E2')]['title'].values

    #Final dataframe which includes all tracks that match the titles of songs chosen date and set
    tracks_from_set = tracks_graph[tracks_graph['title'].isin(set_songs)].copy()

    #Set up empty dictionaries for input into graphs
    graph_data_dict = {}
    graph_highlight_dict = {}

    #Iterate through all songs in the set and add that song to the graph dictionary as the key and a list of all the durations of all times played as the value
    #Repeat for the highlighted shows by returning the same dict but only for the shows in the given range
    for song in set_songs:
        if type == 'Song Duration':
            graph_data_dict[song] = tracks_from_set[tracks_from_set['title'] == song]['duration'].values
            if shows_to_highlight == 'Selected Show':
                graph_highlight_dict[song] = tracks_from_set[(tracks_from_set['title'] == song) & (tracks_from_set['order_id'] == show_id)]['duration'].values
            elif shows_to_highlight == 'Previous 50 Shows':
                graph_highlight_dict[song] = tracks_from_set[(tracks_from_set['title'] == song) & (tracks_from_set['order_id'] < show_id) & (tracks_from_set['order_id'] >= (show_id-50))]['duration'].values
            elif shows_to_highlight == 'Next 50 Shows':
                graph_highlight_dict[song] = tracks_from_set[(tracks_from_set['title'] == song) & (tracks_from_set['order_id'] > show_id) & (tracks_from_set['order_id'] <= (show_id+50))]['duration'].values

        elif type == 'Set Placement':
            graph_data_dict[song] = tracks_from_set[tracks_from_set['title'] == song]['percentintoset'].values
            if shows_to_highlight == 'Selected Show':
                graph_highlight_dict[song] = tracks_from_set[(tracks_from_set['title'] == song) & (tracks_from_set['order_id'] == show_id)]['percentintoset'].values
            elif shows_to_highlight == 'Previous 50 Shows':
                graph_highlight_dict[song] = tracks_from_set[(tracks_from_set['title'] == song) & (tracks_from_set['order_id'] < show_id) & (tracks_from_set['order_id'] >= (show_id - 50))]['percentintoset'].values
            elif shows_to_highlight == 'Next 50 Shows':
                graph_highlight_dict[song] = tracks_from_set[(tracks_from_set['title'] == song) & (tracks_from_set['order_id'] > show_id) & (tracks_from_set['order_id'] <= (show_id + 50))]['percentintoset'].values

    return graph_data_dict, set_songs, graph_highlight_dict
