import streamlit as st


def display_user_favorite_in_sidebar(user_top_track):
    track_id = user_top_track['spotify_uri'].split(':')[-1]
    embed_url = f"https://open.spotify.com/embed/track/{track_id}" if st.session_state['premium'] else user_top_track.get('preview_url')

    iframe_html = f"<iframe src='{embed_url}' width='100%' height='80' frameborder='0' allowtransparency='true' allow='encrypted-media'></iframe>" if st.session_state['premium'] else f"<audio controls><source src='{embed_url}' type='audio/mpeg'>Your browser does not support the audio element.</audio>"

    with st.sidebar:
        st.header("Your Favorite Track")
        st.write(f"{user_top_track['name']} by {user_top_track['artist']}")
        st.markdown(iframe_html, unsafe_allow_html=True)


def display_top_tracks(top_tracks={}):
    if st.session_state['need_login'] == False:
        if 'page' not in st.session_state:
            st.session_state['page'] = 0  
        st.session_state['show_sidebar_player'] = True




        total_tracks = len(top_tracks['items'])
        tracks_per_page = 4 
        total_pages = (total_tracks + tracks_per_page - 1) // tracks_per_page

        start_index = st.session_state['page'] * tracks_per_page
        end_index = min(start_index + tracks_per_page, total_tracks)

        displayed_tracks = top_tracks['items'][start_index:end_index]

        for i in range(0, len(displayed_tracks), 2): 
            row_tracks = displayed_tracks[i:i+2]
            cols = st.columns(2)  
            for col, track in zip(cols, row_tracks):
                track_name = track['name']
                track_artist = track['artists'][0]['name']
                track_image_url = track['album']['images'][0]['url']
                track_uri = track['uri']
                embed_url = f"https://open.spotify.com/embed/track/{track_uri.split(':')[-1]}"

                if st.session_state['premium']:
                    embed_url = f"https://open.spotify.com/embed/track/{track_uri.split(':')[-1]}"
                    iframe_html = f"<iframe src='{embed_url}' width='90%' height='80' frameborder='0' allowtransparency='true' allow='encrypted-media'></iframe>"
                else:
                    preview_url = track.get('preview_url', '#')
                    iframe_html = f"<audio controls><source src='{preview_url}' type='audio/mpeg'>Your browser does not support the audio element.</audio>"

                with col:
                    st.markdown(f"""
                    <div class="card" style="margin: auto; max-width: 400px; margin-bottom: 20px; text-align: center;">
                        <img class="image" src="{track_image_url}" alt="{track_name}" style="width: 100%; height: 400px; object-fit: cover;">
                        <h3>{track_name}</h3>
                        <p>{track_artist}</p>
                        {iframe_html}
                    </div>
                    """, unsafe_allow_html=True)
        # The button styles can be defined in raw CSS and used within the markdown
        button_style = """
            <style>
                .button-style {
                    display: inline-block;
                    padding: 0.5rem 1rem;
                    font-size: 1rem;
                    line-height: 1.5;
                    border-radius: 0.3rem;
                    color: white;
                    background-color: #FA8072;
                    border: none;
                    cursor: pointer;
                }
            </style>
        """

        st.markdown(button_style, unsafe_allow_html=True)

        # The columns can be used to place the buttons in the desired location
        # Adjust the column ratios to suit the alignment needs
        col1, col2, col3 = st.columns([1, 8, 1])

        with col1:
            # Disable the 'Previous' button if on the first page
            if st.button('Previous', disabled=st.session_state['page'] <= 0):
                st.session_state['page'] -= 1
                st.experimental_rerun()

        with col3:
            # Disable the 'Next' button if on the last page
            if st.button('Next', disabled=st.session_state['page'] >= total_pages - 1):
                st.session_state['page'] += 1
                st.experimental_rerun()

        # Optionally, add some space after the buttons
        st.write("")

        # st.balloons()
    else:
        st.markdown("""<span style='font-size: 50px;'>Please log in to see top tracks 😉</span>"""
                        ,unsafe_allow_html=True)