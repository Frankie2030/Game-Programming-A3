# TODO



3. tao nghĩ là cái "3 tam giác trừ máu" nên stuck uer bên trên luôn và trừ 1 lần th, khi nó out khỏi đó đụng lại thì mới trừ típ, hiện tại thì hình như đang 1s trừ 1 máu 
4. tao thấy đạn bắn đang bị chậm, click một cái bay liền thì dễ chơi hơn, chậm ở đây ý t là từ lúc ấn tới lúc thấy viên đạn, còn tốc độ bay chắc ok r
5. tao thấy checkpoint 2 cái lá cờ đầu tiên nó đang kh nằm "giữa 1 block" nào thì phải nhỉ, nó bị lệch so với "vị trí maybe expected của nó"
6. vừa nhảy vừa bắn đang kh đc, hình như chỉ đang nhận event 1 nút keyboard nên kh làm đc đồng thời thì phải 
7. hit boss con boss tròn tròn quay kia đang chưa đúng thì phải thấy dính vòng tròn nhưng kh mất máu
8. con người có năng lượng hả hay sao vậy, tại thấy hình như nếu hết năng lượng bay thì bị trừ máu --> maybe better nếu cho hết năng lượng auto ấn nút flip gravity = nút nhảy thôi, chờ nó hồi đầy thì function nút flip gravity đc hoạt động típ 

10. FUN FACT t nghĩ 2 bài trc mình làm ổn demo ok là do có mode debug lúc nào cx bật, bài này cũng nên có mode debug, hiện hitbox...

12. t thấy có tính năng gì mà ăn chữ cái cục gì xong thì nó miễn nhiễm dame --> theo đề thì mình đã có unique visual, tuy nhiên t chưa thấy timing 
13. t có thấy ăn chữ P tuy nhiên t nghe sound effect chứ t đang chưa hiểu nó để làm gì ?
14. t có thấy mục 5 đề bảo là looping BGM per level --> nên t nghĩ nên tìm 1 background image, scrolling theo screen của mình di chuyển như jetpack
15. t có thấy mục 5 đề bảo là looping BGM per level --> nên t nghĩ cần có >= 2 level, nên nghĩ scenario cho con boss típ theo --> maybe screen size vẫn như bình thường nhưng giờ có 2 con boss và nó di chuyển chứ kh đứng im --> t nghĩ nên hay hơn chứ con boss đó t cũng chưa hỉu lắm vì hiện tại t thấy khi t bắn cục tròn giữa thì lúc thì boss mất máu, lúc thì boss kh mất máu --> những cánh quạt con boss thì nó làm user mất máu nhưng t nghĩ nếu vẫn giữ boss đó thì nên cho nó chắn đạn nữa cx ok 
16. [BONUS] t nghĩ nên có 1 powerup cho user đó là khi nó ăn xong nó đc bắn xuyên chẳng hạn hoặc sấm chớt giết 2 enemy gần nhất ==> anyway t nghĩ nên nhìu quái hơn và có quái nằm giữa không trung cho khó 
17. [BONUS] t nghĩ mình làm 1 cái như vầy thì ăn đc mục bonus thứ 2: màn 2 chẳn hạn, đang di chuyển thì có 1 bức tường chặn nên cho dù có flip cũng kh qua đc --> force user nhảy hoặc bay lên ấn 1 nút để 1 thanh chẳn ngang cầu rơi xuống --> làm cầu bắc qua 1 con sông chẳn hạn --> user rớt xong là dead luôn chứ kh chỉ trừ máu 
18. [BONUS] t nghĩ ăn bonus thứ 3 bằng cách: tăng máu user thành 5 --> khi máu đang còn 2, nếu bị trừ 1 máu thì CAMERA SHAKE hoặc rung hoặc có effect trên màn hình khác với các effect trừ máu hoặc effect khác 
19 [BONUS] mục remappable keys t đang chưa hỉu --> ý thầy là cho user set up key nào functions gì chăn --> nếu hỉu đúng ý này thì maybe mình cho user chỉnh tự do trong a -> z là ok --> trong settings  
20. [NEW BUG] if the boss is not died but you tried to reach the right most, you would be disappeared =)))


# CONCERN (t chưa đọc detail code nên mới có mục này)


21. đề có bảo về gravity --> khi t flip t thấy cảm giác nó bay lên hoặc rơi xuống đều quá, t nghĩ nó phải rơi nhanh dần hoặc bay lên chậm từ từ hay sao đó chứ nhỉ 







# IN PROGRESS



# DONE

- About page not good in UI ==> **Done**

-  map size >= 4 lần screen area này có thể hiện chưa --> t có thấy mapsize nó dài hơn screen area rồi nhma >= 4 lần thì này có ok rồi chưa  ==> **Done: check in the settings.py and see SCREEN_WIDTH = 1280 x SCREEN_HEIGHT = 720 (in settings.py)**

- target resolution trong bài để là 1280 x 720 --> mình thể hiện cái này chưa nhỉ ==> **Done, this is defined in the settings.py**

- Option page the back button not work ==> **DONE**

- tại màn hình retry/pause t nghĩ nên thêm exit (ESC) ==> **DONE with the additional function of save and load the game**

- màn hình mission complete đang bị kh hiển thị đúng (hình như m - nnk - định để  icon thì phải nhưng nó kh load đc) ==> **DONE dep vcl**

