## User接口设计初稿



在所有接口的返回中，增加一个“正确/错误”消息

```json
{
    "status":"success",
    "data": {
        ...
    }
}
```



### 权限系统

计划使用 jwt 作为鉴权方式，涉及到权限相关的行为都需要包含 jwt Header，即需要在 Header 中增加：

`Authorization: Bearer $TOKEN` 其中 `$TOKEN` 即为当前用户的 jwt token



**GET** `user/getuser`

返回当前用户的 id

**POST** `user/login`

登录，期望收到用户名（或者邮箱）、密码，返回 token

**POST** `user/register`

注册，期望收到用户名、（邮箱）、密码，返回 token

**POST** `user/resetpw`

修改密码，期望收到旧密码、新密码，返回 token



增加一个修改全部信息的接口



对于用户的每一个基本信息都提供一个 **POST** 方法，用于修改用户信息，例如：

**POST** `user/updateinfo/name`

修改用户名，期望收到新的用户名，返回成功与否







**用户的不同权限？——普通用户、管理员**

有些复杂



**POST** `user/follow`

关注用户，期望收到要关注的 id，返回成功与否

**POST** `user/unfollow`

取消关注用户，期望收到要取消关注的 id，返回成功与否

**POST** `user/block`

屏蔽用户，期望收到要屏蔽的 id，返回成功与否

**POST** `user/unblock`

取消屏蔽用户，期望收到要取消屏蔽的 id，返回成功与否



**GET** 

获得用户的所有信息（包括非公开信息），要求 token



增加只有管理员才能调用的接口：修改密码、删帖等



### 基本信息

**GET** `user/info/{user_id}`

返回一个 JSON 对象，包括了给定 id 的用户的所有基本公开信息，如下（待定）：

```json
{
    "id": "123",
    "name": "aaa",
    "gender": "male",
    "phone_number": "123",
    "email": "a@a.com",
    "introduction": "good"
}
```



**GET** `user/followed/{user_id}`

返回一个 JSON 对象，是用户的所有 follower 的 id 的数组



**GET** `user/following/{user_id}`

返回一个 JSON 对象，是用户关注的所有其他用户 id 的数组



**GET** `user/blocking/{user_id}`

返回一个 JSON 对象，是用户屏蔽的所有其他用户 id 的数组





