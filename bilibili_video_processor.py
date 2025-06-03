import asyncio
from bilibili_api.video import Video
from bilibili_api.comment import get_comments_lazy, CommentResourceType, OrderType
from bilibili_api.user import User
from bilibili_api.utils.network import Credential

async def get_video_details(bvid: str, credential=None):
    """
    Fetches core video details from Bilibili using its BVid.

    Args:
        bvid (str): The Bilibili video ID (e.g., "BV1SM7HzMEM6").
        credential (Credential, optional): A bilibili_api Credential object for authenticated requests.
                                           Defaults to None (public access).

    Returns:
        dict: A dictionary containing essential video information:
              {
                  'aid': int,  # The video's unique Article ID.
                  'uploader_mid': int,  # The User ID of the video uploader.
                  'cids': list[int]  # A list of Content IDs, one for each part of the video.
              }
              Returns None if fetching fails, data is incomplete, or an error occurs.
    """
    try:
        video = Video(bvid=bvid, credential=credential)
        video_info = await video.get_info()

        if not video_info:
            print(f"Error: Failed to get video info for BVid {bvid}. No data returned from API.")
            return None

        aid = video_info.get('aid')
        owner = video_info.get('owner', {})
        uploader_mid = owner.get('mid')
        pages = video_info.get('pages', [])

        list_of_cids = []
        if pages: # Multi-part video
            for page in pages:
                cid = page.get('cid')
                if cid:
                    list_of_cids.append(cid)
        else: # Single-part video
            cid = video_info.get('cid') # Main CID might be directly on video_info
            if cid:
                list_of_cids.append(cid)

        if not aid or not uploader_mid or not list_of_cids:
            print(f"Error: Missing essential video information (aid, uploader_mid, or cids) for BVid {bvid}. Data: {video_info}")
            return None

        return {'aid': aid, 'uploader_mid': uploader_mid, 'cids': list_of_cids}

    except Exception as e:
        print(f"An error occurred while fetching video details for BVid {bvid}: {e}")
        return None

async def get_top_comment_for_video(aid: int, credential=None):
    """
    Fetches the top (e.g., pinned by uploader) comment for a Bilibili video (identified by AID).

    Args:
        aid (int): The video's Article ID. This is the primary identifier for the comment resource.
        credential (Credential, optional): A bilibili_api Credential object. Defaults to None.

    Returns:
        dict: A dictionary containing the top comment's details:
              {
                  'commenter_uname': str,  # Username of the commenter.
                  'comment_message': str   # Content of the comment.
              }
              Returns None if no pinned/top comment is found, or if an error occurs during fetching.

    Note on comment fetching logic:
    This function searches for comments that are explicitly marked as "top" by the uploader or platform administrators
    (e.g., via `reply['control']['is_up_top']` or `reply['assist'] == 2`). It also checks a specific 'top' field
    in the API response structure that sometimes contains admin-set top comments.
    Comments are fetched ordered by time (`OrderType.TIME`) by default.
    """
    try:
        comment_data = await get_comments_lazy(oid=aid, type_=CommentResourceType.VIDEO,
                                               order=OrderType.TIME, credential=credential)

        if not comment_data:
            # print(f"Debug: No comment_data structure returned for AID {aid}") # For deeper debugging
            return None

        # Check for specific admin/uploader set "top" reply (often found in data['top']['replies'])
        if 'top' in comment_data and comment_data['top'] and \
           'replies' in comment_data['top'] and comment_data['top']['replies']:
            top_admin_reply_data = comment_data['top']['replies']
            if isinstance(top_admin_reply_data, list) and len(top_admin_reply_data) > 0:
                top_admin_reply = top_admin_reply_data[0]
            elif isinstance(top_admin_reply_data, dict):
                 top_admin_reply = top_admin_reply_data
            else:
                top_admin_reply = None

            if top_admin_reply and top_admin_reply.get('content') and top_admin_reply.get('member'):
                return {
                    'commenter_uname': top_admin_reply['member'].get('uname', 'Unknown Uploader'),
                    'comment_message': top_admin_reply['content'].get('message', '')
                }

        replies = comment_data.get('replies', [])
        if not replies:
            # print(f"Debug: No 'replies' list found or empty for AID {aid}") # For deeper debugging
            return None

        for reply in replies:
            if not reply:
                continue

            is_pinned_by_control = reply.get('control', {}).get('is_up_top', False)
            is_assist_top = reply.get('assist') == 2

            if is_pinned_by_control or is_assist_top:
                content = reply.get('content', {}).get('message', '')
                uname = reply.get('member', {}).get('uname', 'Unknown Uploader')
                return {'commenter_uname': uname, 'comment_message': content}

        # print(f"Debug: No comment met top criteria for AID {aid}") # For deeper debugging
        return None # No top/pinned comment found after checking all sources

    except Exception as e:
        print(f"An error occurred while fetching top comment for video AID {aid}: {e}")
        return None

async def get_uploader_creation_time(uploader_mid: int, credential=None):
    """
    Fetches the account creation time of a Bilibili user.

    Args:
        uploader_mid (int): The User ID (mid) of the uploader.
        credential (Credential, optional): A bilibili_api Credential object. Defaults to None.

    Returns:
        dict: A dictionary containing the user's account creation time and an optional message.
              Example for valid time: {'creation_time': 1234567890, 'message': 'Timestamp in seconds since epoch.'}
              Example for zero/None time: {'creation_time': 0, 'message': 'Account creation time reported as 0 or unavailable.'}
              Returns None if an API error occurs during fetching.
    """
    try:
        user = User(uid=uploader_mid, credential=credential)
        user_info = await user.get_user_info()

        if not user_info:
            print(f"Error: Failed to get user info for MID {uploader_mid}. No data returned from API.")
            return None

        creation_timestamp = user_info.get('jointime')
        if creation_timestamp is None: # Check if 'jointime' is missing
            creation_timestamp = user_info.get('regtime') # Fallback to 'regtime'

        if creation_timestamp == 0:
            return {'creation_time': 0, 'message': 'Account creation time reported as 0 (Jan 1, 1970 UTC).'}
        elif creation_timestamp is not None: # Non-zero timestamp
            return {'creation_time': creation_timestamp, 'message': 'Unix timestamp (seconds since epoch).'}
        else: # Timestamp is None even after checking fallbacks
            # This case might be redundant if 'jointime' or 'regtime' always exist but can be 0.
            # However, explicit handling for None is safer.
            print(f"Warning: Could not find 'jointime' or 'regtime' in user info for MID {uploader_mid}. Data: {user_info}")
            return {'creation_time': None, 'message': 'Account creation time field not found in API response.'}


    except Exception as e:
        print(f"An error occurred while fetching user info for MID {uploader_mid}: {e}")
        return None

async def process_videos(bvid_list: list, credential=None):
    """
    Processes a list of Bilibili videos (by BVid) to fetch and display their details,
    uploader's creation time, and the top comment for each video.

    Args:
        bvid_list (list[str]): A list of Bilibili Video IDs (BVIDs) to process.
        credential (Credential, optional): A bilibili_api Credential object for authenticated requests.
                                           Defaults to None for public access attempts.

    Output:
        Prints processed information for each video to standard output. This includes
        the video's AID, uploader's MID, uploader's account creation time (with context),
        and any found top comment. Errors during fetching are also reported.
    """
    for bvid in bvid_list:
        print(f"Processing BVID: {bvid}")
        video_details = await get_video_details(bvid, credential)

        if not video_details:
            print(f"  Could not fetch video details for BVID: {bvid}. Skipping.\n")
            continue

        aid = video_details['aid']
        uploader_mid = video_details['uploader_mid']

        print(f"  Video AID: {aid}")
        print(f"  Uploader MID: {uploader_mid}")

        uploader_time_info = await get_uploader_creation_time(uploader_mid, credential)

        if uploader_time_info:
            time_val = uploader_time_info.get('creation_time')
            time_msg = uploader_time_info.get('message', 'Timestamp details unavailable.')
            if time_val is not None:
                 print(f"  Uploader Creation Time: {time_val} ({time_msg})")
            else: # Only message, time is None
                 print(f"  Uploader Creation Time: {time_msg}")
        else:
            print(f"  Uploader Creation Time: Not found due to an earlier error or API issue.")

        top_comment_info = await get_top_comment_for_video(aid, credential)
        if top_comment_info:
            comment_display = f"[{top_comment_info['commenter_uname']}] \"{top_comment_info['comment_message']}\""
            print(f"  Top Comment: {comment_display}")
        else:
            print(f"  Top Comment: No specific top comment found, or an error occurred while fetching.")

        print("-" * 40 + "\n")


if __name__ == '__main__':
    # --- Credential Setup ---
    # Provide your Bilibili cookie values here.
    # SESSDATA and bili_jct are generally most important for authenticated actions.
    # buvid3, buvid4, and DedeUserID can be relevant for certain API endpoints or for anti-bot measures.
    sessdata_cookie = "11306cc8%2C1764304425%2Cd1dce%2A62CjDvnHQJStQDioilDcjECvyWYqa4Sl-V6nxuZdyZ3VYy-y4MD1J5Ew_cdfcWiK9MvLkSVk1WM2FrSlk2YjQ5MWF1bzExNVdUSGlRVHhVc0RCUlF2b2J1NndxUXM2QmVXUnhwZjdtWmFlcEZ2VFNsYW5TUm5jMnhXYXFJTmdnSDBNSDlMdGVMNy13IIEC"
    bili_jct_cookie = "29fe775e683aa9c52fc7cec18a19ed2c"
    dedeuserid_cookie = "3546738960894522"
    buvid3_cookie = "3825E45A-1BB2-9F20-45BB-F8BAD67A5AF087460infoc"
    # buvid4_cookie = "5FE5CD10-31CF-66B0-62E3-FEC3F74CCF1588907-025053110-r7AB6RB7mOZSK4Yzg7TPIA8MxLhr1Y43g4RPYwSq41OjJEvQv%2Fwixj74PoBnLupY" # Often optional if buvid3 is set

    # Create the Credential object for API calls
    # Ensure DedeUserID is passed as a string if the library expects it as such.
    credential_object = Credential(
        sessdata=sessdata_cookie,
        bili_jct=bili_jct_cookie,
        buvid3=buvid3_cookie,
        dedeuserid=str(dedeuserid_cookie)
    )

    # --- Video Processing ---
    # List of Bilibili Video IDs (BVIDs) to process.
    # BV1SM7HzMEM6 is used as the example here.
    sample_bvid_list = ["BV1SM7HzMEM6"]

    print("Starting Bilibili video processing with provided credentials...")
    asyncio.run(process_videos(sample_bvid_list, credential=credential_object))
    print("Processing complete.")
