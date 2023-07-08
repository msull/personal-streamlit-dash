import extra_streamlit_components as stx
import streamlit as st
from auth_helpers import LoginRequired, save_auth_db, set_page_config

try:
    authenticator, username = set_page_config("Home", requires_auth=True)
except LoginRequired:
    pass
else:

    def main():
        navbar, profile = st.columns((3, 1))

        with profile:
            authenticator.logout("Logout", "main")

        st.header(f"Welcome *{username}*")
        st.write("Choose a page from the left")

        try:
            if authenticator.reset_password(username, "Reset password"):
                st.success("Password modified successfully")
                save_auth_db(authenticator)
        except Exception as e:
            st.error(e)

        with st.expander("Session Data"):
            st.write(dict(sorted(st.session_state.items())))
        with st.expander("Cookies"):
            cookie_mgr = stx.CookieManager("asdf")
            st.json(cookie_mgr.get_all())

        # # Creating a password reset widget
        # try:
        #     if authenticator.reset_password(username, "Reset password"):
        #         st.success("Password modified successfully")
        # except Exception as e:
        #     st.error(e)
        # try:
        #     if authenticator.update_user_details(username, "Update user details"):
        #         st.success("Entries updated successfully")
        # except Exception as e:
        #     st.error(e)

    main()
