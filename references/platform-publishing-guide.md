# Platform Publishing Guide

What you need to actually publish to each major platform. Use this when you're ready to move past draft mode and wire up real publish adapters.

This doc is intentionally specific. Generic "publish via the API" advice is useless; each platform has its own rate limits, authentication ceremonies, and content-type quirks that you'll hit immediately.

## Meta (Instagram + Facebook)

### Authentication

- Meta Business account + Meta App + Instagram Business or Creator account linked
- Generate a System User access token at the Business Manager level (these don't expire)
- Required scopes: `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`

### Endpoints

```
# Create a media container
POST https://graph.facebook.com/v18.0/{ig-user-id}/media
  ?image_url=URL
  &caption=TEXT
  &access_token=TOKEN

# Publish the container
POST https://graph.facebook.com/v18.0/{ig-user-id}/media_publish
  ?creation_id=CONTAINER_ID
  &access_token=TOKEN
```

For videos / reels:

```
POST https://graph.facebook.com/v18.0/{ig-user-id}/media
  ?media_type=REELS
  &video_url=URL
  &caption=TEXT
```

### Rate limits

- 25 posts per IG account per 24 hours
- 200 API calls per hour per user

### Gotchas

- The video URL must be publicly accessible from Meta's IPs. CDN-hosted is fine. localhost is not.
- The video must complete uploading and processing before `media_publish`. Poll the container's `status_code` until it returns `FINISHED`.
- Reels require specific dimensions (9:16) and length (1-90s). Outside that, the API rejects with a useless error.
- Caption max: 2,200 characters.
- Hashtag max: 30 per post.

### Stories

Stories have a separate endpoint and a 24-hour lifespan:

```
POST https://graph.facebook.com/v18.0/{ig-user-id}/media
  ?media_type=STORIES
  &image_url=URL
```

You cannot publish to Facebook Stories programmatically — that's an Instagram-only capability.

## X / Twitter

### Authentication

X v2 API. Requires:

- X Developer account
- Project + App created
- OAuth 2.0 Bearer Token for app-only, or user context tokens for user-level posting

API access is paid as of 2024 onward. Basic tier is $100/mo and rate-limited.

### Endpoints

```
POST https://api.x.com/2/tweets
  Headers: Authorization: Bearer USER_TOKEN
  Body: { "text": "post text" }
```

For media (requires v1.1 upload API + v2 tweet API):

```
# Step 1: upload media via v1.1
POST https://upload.twitter.com/1.1/media/upload.json
  Body: media=<binary>

# Step 2: tweet with the media ID
POST https://api.x.com/2/tweets
  Body: { "text": "...", "media": { "media_ids": ["123"] } }
```

### Rate limits

- 200 posts per 24 hours (Basic plan)
- 100 user lookups per 15 min

### Gotchas

- The 280-character limit counts URLs as 23 chars regardless of actual length
- Media types: images (up to 4), one video, or one GIF — never mixed
- Video: 512MB max, 2:20 length, MP4 H.264
- Threads: post the first tweet, then post a reply with `in_reply_to_tweet_id`

## LinkedIn

### Authentication

- LinkedIn Developer account
- Marketing Developer Platform (apply, takes ~2 weeks)
- OAuth 2.0 with `w_member_social` scope for personal posting, `w_organization_social` for company pages

### Endpoints

```
POST https://api.linkedin.com/v2/ugcPosts
  Headers: Authorization: Bearer TOKEN, X-Restli-Protocol-Version: 2.0.0
  Body:
  {
    "author": "urn:li:person:USER_ID",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
      "com.linkedin.ugc.ShareContent": {
        "shareCommentary": { "text": "post text" },
        "shareMediaCategory": "NONE"
      }
    },
    "visibility": {
      "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
  }
```

For images / videos: upload to `/assets?action=registerUpload` first, then attach by URN.

### Rate limits

- 150 posts per user per 24 hours
- Strict throttling on bulk operations

### Gotchas

- LinkedIn's API is notoriously slow to approve. Plan 2+ weeks of waiting for Marketing API access.
- The text field on personal posts is limited to 3,000 characters.
- Polls, articles, and "documents" each have their own separate API surfaces.
- LinkedIn aggressively penalizes "engagement bait." Don't publish content that violates their community guidelines via API — they will revoke your access.

## TikTok

### Authentication

- TikTok for Developers account
- App approved for posting (their bar is high; expect 2-4 weeks)
- Content Posting API access

### Endpoints

```
POST https://open.tiktokapis.com/v2/post/publish/video/init/
  Headers: Authorization: Bearer USER_TOKEN
  Body:
  {
    "post_info": {
      "title": "caption",
      "privacy_level": "PUBLIC_TO_EVERYONE",
      "disable_duet": false,
      "disable_comment": false
    },
    "source_info": {
      "source": "PULL_FROM_URL",
      "video_url": "https://your-cdn.com/video.mp4"
    }
  }
```

### Rate limits

- 6 posts per user per 24 hours
- Burst limits within shorter windows

### Gotchas

- TikTok's API approval is the hardest of the major platforms
- Vertical videos only (9:16), 5-60 seconds
- Captions: 150 chars on iOS, 2,200 on Android — keep to 150 to be safe
- Sound is critical — TikTok deprioritizes silent videos in the algorithm

## Threads

As of late 2026:

- Public posting API exists via the Meta Graph API (similar to IG)
- Requires the same auth as Meta IG/FB
- Endpoint: `POST /v18.0/{user-id}/threads`

Threads is a younger API surface — expect frequent changes.

## Bluesky

The newest, the cleanest:

- AT Protocol open standard
- No app approval required
- Authentication via app password (per-account secret)

```
POST https://bsky.social/xrpc/com.atproto.repo.createRecord
  Body:
  {
    "collection": "app.bsky.feed.post",
    "repo": "did:plc:YOUR_DID",
    "record": {
      "text": "post text",
      "createdAt": "2026-05-12T14:30:00Z"
    }
  }
```

### Rate limits

- Generous compared to commercial platforms
- ~5,000 actions per hour per user

## Storage layer

Every platform expects publicly-accessible URLs for media. The skill assumes you have one of:

- **Vercel Blob** — `$0.15/GB storage, $0.30/GB egress`. Easiest if you're already on Vercel.
- **S3 / Cloudflare R2** — $0.015/GB storage, free egress on R2. Cheapest at scale.
- **Imgix / Cloudinary** — adds transformation features. Higher cost.

The skill's `scripts/upload-temp-file.sh` handles upload to Vercel Blob with fallbacks. Add more as you need.

## Adapter pattern

For the production upgrade, build one adapter per platform with the same interface:

```python
class PublishAdapter:
    def publish(self, post: Post) -> PublishResult:
        """Submit the post to the platform.
        Returns success status, platform post ID, and any errors.
        """

class MetaAdapter(PublishAdapter):
    def publish(self, post):
        # 1. Upload media to Meta
        # 2. Create container
        # 3. Poll for FINISHED status
        # 4. Publish container
        # 5. Return platform post ID

class XAdapter(PublishAdapter):
    def publish(self, post):
        # 1. Upload media via v1.1
        # 2. Post tweet via v2 with media_id
        # 3. Return platform post ID
```

Each adapter handles platform-specific quirks. The skill's main loop just calls `adapter.publish(post)` and doesn't care what's inside.

## Audit logging

For every publish, log:

| Field | Notes |
|---|---|
| `post_id` | Your internal ID |
| `platform` | Which adapter ran |
| `published_at` | Server timestamp |
| `platform_post_id` | The ID returned by the platform |
| `platform_url` | Direct URL to the post |
| `status` | `success` / `failure` |
| `error_message` | If failure |
| `request_payload_hash` | Hash of the payload sent |

This log is what lets you debug "did we publish that?" disputes weeks later. Don't skip it.

## Rollback strategy

If a publish goes out wrong:

1. The skill should fail toward NOT publishing rather than publishing duplicates
2. Idempotency on the queue level — same `post_id` can't be processed twice
3. If you do need to retract: most platforms have a delete endpoint. Add a `unpublish(platform_post_id)` method to each adapter and a manual operator-triggered flow to invoke it.

You'll need this eventually. Build it early.
