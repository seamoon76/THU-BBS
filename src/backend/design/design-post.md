### 信息模块接口设计

~~后面为了顺口可能会把信息称作帖子~~

标有 ! 的接口，需要jwt认证，具体做法为在 header 中增加

```
Authorization: Bearer $TOKEN
```

其中，`$TOKEN` 的值需要使用 `/user/login` 方法获取

#### 

**POST** `/post/barequery`

返回所有筛选的信息，使用post方法，需要传递参数以供后端筛选和分页，这些参数如下

```json
{
    "filter_by":"string",
    "filter_parameter":"string",
    "order_by":"string",
    "order":"string(asc/desc)",
    "skip":"int",
    "limit":"int"
}
```

比如查询某一用户的帖子，就是 filter by user，filter parameter 就是用户 id。当然不排除实现的时候遇到其他问题，导致把按部分筛选的接口单独分出来。

对于 `skip` 和 `limit` 的分页方式，暂定为获取第 21-30 条数据时，skip=20，limit=10

返回的就是帖子 id 的列表，大概会是这样

```json
{
	"posts":[
		{
			"id":123
			// 这里面需不需要一些其他信息？ //
		},
		{
			"id":456
		}
	]
}
```



**！POST** `/post/query`

从上一个接口包装出来的一个新的接口，需要用户jwt，返回的帖子中不包含用户已经屏蔽的内容



**GET** `/post/{post_id}`

获得信息的所有内容，返回的内容这样如何

```json
{
 	"title": "string",
    "id":123,
    "content": "string",
    "create_at": "2001-12-01 18:30 (不一定是这个格式)",
    "user_id":456,
    "like_num":123,
    "star_num":123,
    "comment_num":123,
    "resources":[
        {
            id:234,
            "type": "picture",
            "url": "11.11.11.11/resource/abcd"
        },
        {
            id:123,
            "type": "video",
            "url": "11.11.11.11/resource/efg"
        },
    ]
}
```



**！POST** `/post`

用户创建一个信息，需要

```json
{
    title: "string",
    content: "string",
    resources: [
        {
            "id":11
        },
        {
            "id":23
        },
        // 会有一个接口用来上传资源，这个接口返回资源的各种属性
    ],
    // 可能还有其他属性，例如定位等
}
```



**GET** `/post/{post_id}/comment`

获得信息的所有评论，返回这些

```json
{
    id: 1,
    user_id: 345,
    user_name: "name",
    avatar_url: "aaa",
    content: "good"
}
```



**！POST**  `/post/{post_id}/comment`

发表评论，参数

```json
{
    content: "good"
}
```





**GET** `/user/{user_id}/star`

获取用户收藏的信息



**！POST** `/post/star`

收藏信息，参数为

```json
{
    "id":123 //信息的id
}
```



**！POST** `/post/like`

点赞信息，和收藏一样



