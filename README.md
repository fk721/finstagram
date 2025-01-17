# Features Implemented on Part 3

## View Visible Photos

```sql
(SELECT P.photoID, P.postingdate, P.photoBlob, P.caption, P.photoPoster
FROM Photo P JOIN Follow F ON (P.photoPoster = F.username_followed)
WHERE followstatus = True AND allFollowers = True
AND username_follower = %s)

UNION

(SELECT photoID, postingdate, photoBlob, caption, photoPoster
FROM Photo
WHERE photoID IN
(SELECT photoID
FROM BelongTo B JOIN SharedWith S ON ((B.owner_username = S.groupOwner) AND (B.groupName = S.groupName))
AND member_username = %s))

UNION

(SELECT photoID, postingdate, photoBlob, caption, photoPoster
FROM Photo
WHERE photoPoster = %s)

ORDER BY postingdate DESC;
```
To view visible photos, I execute three queries that I later union together.

The first query selects Photos posted by a user that the current user in the session follows; allFollowers for this photo is True, and followstatus is True.

The second query selects Photos that were shared with a friend group that a user is in.

Although it was not mentioned, I thought it made sense for a user to see their own posts on their feed (just like Instagram), hence the third query.

The full code for this can be found in _app.py_ under the route _/home_.

## View Further Photo Info

#### Finding the firstName, lastName of the photoPoster on a photo

```sql
SELECT firstName, lastName, photoID 
FROM Photo JOIN Person ON (Photo.photoPoster = Person.username)
WHERE photoID = %s
```

#### Finding the username, first name, last name of the people who have been tagged on a photo

```sql
SELECT username, firstName, lastName
FROM Tagged JOIN Person USING(username)
WHERE tagstatus = True AND photoID = %s
```

#### Finding the username and rating of those who have liked a photo

```sql
SELECT username, rating 
FROM Likes
WHERE photoID
```

#### Finding the number of a likes on a photo

```sql
SELECT count(*) AS numLikes
FROM Likes
WHERE photoID = %s
```

The full code for this can be found in _app.py_ under the route _/get\_info_.

## Post a Photo

I decided to add a BLOB attribute to the Photo model which stores the photo represented as a binary object. I first convert the photo into a base 64 object, and then store it into the database. 

The full code for this can be found in _app.py_ under the routes _/upload_ and _/upload\_image_.

## Manage Follows

The full code for this can be found in _app.py_ under the routes */follow*, */followUser*, */follow-requests*, and */view-followers*.

## Optional Features

For the final part of the project, I plan on implementing the following two features:

- **Search by tag**: Search for photos that are visible to the user and that tag some particular person (the user or someone else)
- **Search by poster:** Search for photos that are visible to the user and that were posted by some particular person (the user or someone else)

### A Note on the Demo

The demo named _finstagram-demo.mp4_ shows the features I have already implemented. When it came to friendsgroups and tags/likes, I already wrote some SQL inserts to test my features, which is demonstrated by the video.

