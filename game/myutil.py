# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 21:55:58 2017

@author: ChenXiao XuGang
"""
import numpy as np
import Queue
import  copy
#from myclass import Moves
import random


#展示扑克函数
def card_show(cards, info, n):
    
    #扑克牌记录类展示
    if n == 1:
        print info
        names = []
        for i in cards:
            names.append(i.name+i.color)
        print names    
    #Moves展示
    elif n == 2:
        if len(cards) == 0:
            return 0
        print info
        moves = []
        for i in cards:
            names = []
            for j in i:
                names.append(j.name+j.color)
            moves.append(names)
        print moves    
    #record展示
    elif n == 3:
        print info
        names = []
        for i in cards:
            tmp = []
            tmp.append(i[0])
            tmp_name = []
            #处理要不起
            try:
                for j in i[1]:
                    tmp_name.append(j.name+j.color)
                tmp.append(tmp_name)
            except:
                tmp.append(i[1])
            names.append(tmp)
        print names
       

#在Player的next_moves中选择出牌方法
def choose(next_move_types, next_moves, last_move_type,cards_left,last_move , model):
    '''
    开局start 的时候打牌策略
    '''
    if last_move_type=="start":

        return choose_start_policy(next_move_types, next_moves, last_move_type,cards_left,last_move)
        #return get_card_CombInfo(cards_left)
    elif last_move_type=="buyao" or last_move_type=="yaobuqi":
        pass
    else:
        '''
        上家出牌时候的打牌策略
        '''
        return choose_orplay_policy(cards_left, last_move_type,last_move,next_move_types, next_moves)
    

     


'''
#对出牌类型进行排序
王炸>炸>
王炸 → 炸弹 → 单顺 → 双顺 → 三顺 → 三条 → 一对 → 单张
["dan", "dui", "san", "san_dai_yi", "san_dai_er", "shunzi"]
'''
def MoveTypeRank(next_move_types):
    type_rank=dict()
    for i in next_move_types:
        type_rank.get(i,0)
        if i=='dan':
            type_rank[i]=0
        if i=="dui":
            type_rank[i]=1
        if i=="san_dai_yi":
            type_rank[i]=2
        if i=="san":
            type_rank[i]=3
        if i=="san_dai_er":
            type_rank[i]=4
        if i=="shunzi":
            type_rank[i]=5
        if i=="bomb":
            type_rank[i]=6
            
    return type_rank



###AI策略选择



def get_card_CombInfo(cards_left,last_move_type,last_move):
    # 出牌信息
    dan = []
    dui = []
    san = []
    san_dai_yi = []
    san_dai_er = []
    bomb = []
    shunzi = []

    # 牌数量信息 用字典统计牌的数量
    card_num_info = {}
    # 牌顺序信息,计算顺子
    card_order_info = []
    # 王牌信息
    king = []

    # 下次出牌
    next_moves = []
    # 下次出牌类型
    next_moves_type = []

    # 统计牌数量/顺序/王牌信息
    for i in cards_left:
        # 王牌信息
        if i.rank in [14, 15]:
            king.append(i)
        # 数量
        tmp = card_num_info.get(i.name, [])
        if len(tmp) == 0:
            card_num_info[i.name] = [i]  #字典的key 对应的value是牌面为key的List
        else:
            card_num_info[i.name].append(i)
        # 顺序
        if i.rank in [13, 14, 15]:  # 不统计2,小王,大王
            continue
        elif len(card_order_info) == 0:
            card_order_info.append(i)
        elif i.rank != card_order_info[-1].rank:
            card_order_info.append(i)

    # 王炸
    if len(king) == 2:
        bomb.append(king)

    # 出单,出对,出三,炸弹(考虑拆开)
    while card_num_info:

        for k, v in card_num_info.items():



            if len(v) == 4:
                bomb.append(v)
                card_num_info.pop(k)
                break
            elif len(v) == 3:
                san.append(v)
                card_num_info.pop(k)
                break
            elif len(v) == 2:
                dui.append(v)
                card_num_info.pop(k)
                break
            elif len(v) == 1:
                dan.append(v)
                card_num_info.pop(k)
                break


    # 三带一,三带二
    for san_ in san:
        for dan_ in dan:
            # 防止重复
            if dan_[0].name != san_[0].name and dan_[0].name not in ["1","2","14","15"]:
                san_dai_yi.append(san_ + dan_)
        for dui_ in dui:
            # 防止重复
            if dui_[0].name != san_[0].name and dui_[0].name not in ["1","2","14","15"]:
                san_dai_er.append(san_ + dui_)
#======================================================================================
    if last_move_type=="start":

        moves_types = ["dan", "dui", "san", "san_dai_yi", "san_dai_er", "shunzi"]
        i = 0
        for move_type in [dan, dui, san, san_dai_yi,
                          san_dai_er, shunzi]:
            for move in move_type:
                if move in ['dan',"dui","san","bomb"]:
                    next_moves.append([move])
                    next_moves_type.append(moves_types[i])
                else:

                    next_moves.append(move)
                    next_moves_type.append(moves_types[i])
            i = i + 1

        #return next_moves,next_moves_type

        # 出单
    elif last_move_type == "dan":
        for move in dan:
            # 比last大
            if move[0].bigger_than(last_move[0]):
                next_moves.append(move)
                next_moves_type.append("dan")
    # 出对
    elif last_move_type == "dui":
        for move in dui:
            # 比last大
            if move[0].bigger_than(last_move[0]):
                next_moves.append(move)
                next_moves_type.append("dui")

    # 出三个
    elif last_move_type == "san":
        for move in san:
            # 比last大
            if move[0].bigger_than(last_move[0]):
                next_moves.append(move)
                next_moves_type.append("san")
    # 出三带一
    elif last_move_type == "san_dai_yi":
        for move in san_dai_yi:
            # 比last大
            if move[0].bigger_than(last_move[0]):
                next_moves.append(move)
                next_moves_type.append("san_dai_yi")
    # 出三带二
    elif last_move_type == "san_dai_er":
        for move in san_dai_er:
            # 比last大
            if move[0].bigger_than(last_move[0]):
                next_moves.append(move)
                next_moves_type.append("san_dai_er")
    # 出炸弹
    elif last_move_type == "bomb":
        for move in self.bomb:
            # 比last大
            if move[0].bigger_than(last_move[0]):
                next_moves.append(move)
                next_moves_type.append("bomb")
    # 出顺子
    elif last_move_type == "shunzi":
        for move in shunzi:
            # 相同长度
            if len(move) == len(last_move):
                # 比last大
                if move[0].bigger_than(last_move[0]):
                    next_moves.append(move)
                    next_moves_type.append("shunzi")
    else:
        print "last_move_type_wrong"

    # 除了bomb,都可以出炸
    if last_move_type != "bomb":
        for move in bomb:
            next_moves.append(move)
            next_moves_type.append("bomb")

    return next_moves_type, next_moves

def choose_start_chupai(cards_left,last_move_type,last_move):
    next_moves, next_moves_type=get_card_CombInfo(cards_left,last_move_type,last_move)
    return next_moves, next_moves_type


def choose_start_policy(next_move_types, next_moves, last_move_type,cards_left,last_move):
    #要不起

    chupai_order_dict={"dan":0, "dui":1, "san":3, "san_dai_yi":2, "san_dai_er":4, "shunzi":5,"bomb":6}

    card_show(next_moves,'choose_start_policy：：next moves: ',2)
    '''
        如果是start ，那么就出最小的move_type
        如果上家出牌的话，下家的牌的类型和上家是一样的

         poss_types,poss_moves是不拆牌情况下的下一步可能组合

    '''

    poss_types,poss_moves =get_card_CombInfo(cards_left,last_move_type,last_move)
    card_show(poss_moves,"choose_start_policy：：fan hui ka pai",2)
    #next_move_types_ranks=MoveTypeRank(poss_types)
    #follow_move_type=CheckNextPaiType(next_move_types_ranks)
    follow_move_type=CheckNextPaiType(poss_types)

    follow_move=CheckNextPaiValue(poss_types,follow_move_type,poss_moves)
    card_show(follow_move, 'choose_start_policy::next move: ', 1)
    return follow_move_type, follow_move
            


def choose_orplay_policy(cards_left, last_move_type,last_move,next_move_types, next_moves):
    '''
            如果上家出牌的话，下家的牌的类型和上家是一样的

             poss_types,poss_moves是不拆牌情况下的下一步可能组合

    '''
    poss_types, poss_moves = get_card_CombInfo(cards_left,last_move_type,last_move)

    card_show(poss_moves,"choose_orplay_policy::posssible move",2)

    '''
        如果上家出牌的话，下家的牌的类型和上家是一样的

        如果上家不要的话，自己要的起的话  
    '''

    follow_move_type = last_move_type
    follow_move = CheckNextPaiValue(poss_types, follow_move_type, poss_moves)

    print "choose_orplay_policy:: follow_move_type,poss_types", follow_move_type, " ", poss_types


    if len(poss_moves) == 0:
        #不拆牌情况下要不起的话，就考虑拆牌
        follow_move = CheckNextPaiValue(next_move_types, follow_move_type, next_moves)
        if len(follow_move)==0 or follow_move_type not in poss_types:
            return "yaobuqi", []
            #return "yaobuqi", "yaobuqi"
    if poss_types == ["bomb"] or poss_types == "bomb":
        if len(cards_left)<=6:
            follow_move_type="bomb"
            #因为poss_move套了两个list
            follow_move=poss_moves[0]
        else:
            return "yaobuqi", []
    return follow_move_type, follow_move




def CheckNextPaiType(poss_types_tmp):
    # 把符合出牌类型的牌放到一个列表里
    # 根据牌的rank,找出最小牌的位置，并把它设置为 next_move
    next_move_types_ranks={}
    chupai_order_dict={"dan":0, "dui":1, "san":4, "san_dai_yi":3, "san_dai_er":5, "shunzi":2,"bomb":6}
    for i in poss_types_tmp:
        val=chupai_order_dict.get(i)
        next_move_types_ranks[i]=val
    # 如果要出牌的话，要出next_move_types_ranks最小的一个
    min_idx = 100
    max_idx = 0

    # ========================返回最小出牌类型===========================
    follow_move_type=None

    for i, j in next_move_types_ranks.items():

        if j < min_idx:
            min_idx = j
        if j > max_idx:
            max_idx = j

    for i, j in chupai_order_dict.items():
        if j == min_idx:
            follow_move_type = i

    print "CheckNextPaiType：：follow_move_type: ", follow_move_type

    '''
    rlst0=["dan", "dui", "shunzi", "san"]
    rlst=[]
    for it in rlst0:
        if it in next_move_types_ranks:
            rlst.append(it)


    if follow_move_type in rlst0 and len(rlst)!=0:
        rdx=random.randint(0,len(rlst))
        follow_move_type=rlst[rdx]
    '''
    #避免每次start都是出单
    if follow_move_type=="dan" and "dui" in poss_types_tmp and "san_dai_yi" in poss_types_tmp:
        rdx = random.randint(0, 2)
        blst = ["dan", "dui","san"]
        follow_move_type = blst[rdx]
    elif follow_move_type=="dan" and "dui" in poss_types_tmp:
        rdx = random.randint(0, 1)
        clst = ["dan", "dui"]
        follow_move_type = clst[rdx]


    return follow_move_type

def CheckNextPaiValue(next_move_types,follow_move_type,next_moves):

#==========================================================================
    #如果是“对、三、炸”的
    next_move=None
    mlst=[]
    if follow_move_type in ["dan","dui","san","san_dai_yi","san_dai_er","bomb"]:
        #筛选出满足follow_move_type类型的牌的组合
        next_op_lst = []
        for j in range(len(next_moves)):
            if next_move_types[j] == follow_move_type:
                next_op_lst.append(next_moves[j])

        #进行牌面的比较
        idx=0
        for move in next_op_lst:
            # 比last大
            if idx==0:
                mlst.append(move)
            #bigger_than比较了card rank，所一不用考虑1和2的情况
            if mlst[0][0].bigger_than(move[0]):
                mlst.pop()
                mlst.append(move)
            idx+=1
        #返回可以出牌的组合里最小的move
        if len(mlst):
            next_move=mlst.pop()
        else:
            next_move=[]
    return next_move


    






#发牌
def game_init(players, playrecords, cards):
    
    #洗牌
    np.random.shuffle(cards.cards)
    #排序
    p1_cards = cards.cards[:18]
    p1_cards.sort(key=lambda x: x.rank)
    p2_cards = cards.cards[18:36]
    p2_cards.sort(key=lambda x: x.rank)
    p3_cards = cards.cards[36:]
    p3_cards.sort(key=lambda x: x.rank)
    players[0].cards_left = playrecords.cards_left1 = p1_cards
    players[1].cards_left = playrecords.cards_left2 = p2_cards
    players[2].cards_left = playrecords.cards_left3 = p3_cards

