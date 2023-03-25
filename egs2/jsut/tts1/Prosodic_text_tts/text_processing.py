#!/usr/bin/env python3

import numpy as np
import re
import pyopenjtalk
import jaconv

#各条件を正規表現で表す
c1 = '[ウクスツヌフムユルグズヅブプヴ][ァィェォ]' #ウ段＋「ァ/ィ/ェ/ォ」
c2 = '[イキシチニヒミリギジヂビピ][ャュェョ]' #イ段（「イ」を除く）＋「ャ/ュ/ェ/ョ」
c3 = '[テデ][ィュ]' #「テ/デ」＋「ャ/ィ/ュ/ョ」
c4 = '[ァ-ヴー^＾,.、。？！!?]' #カタカナ１文字（長音含む）

cond = '('+c1+'|'+c2+'|'+c3+'|'+c4+')'
re_mora = re.compile(cond)

def moraWakachi(kana_text):
    return re_mora.findall(kana_text)

def accent_phrase(text):
    import pyopenjtalk
    import re
    

    phones = []
    prev=-1
    phrase_len=[]
    accent_idx=[]
    kata=pyopenjtalk.g2p(text,kana=True)
    
    mora = moraWakachi(kata)
    for labels in pyopenjtalk.run_frontend(text)[1]:
        if labels.split("-")[1].split("+")[0] == "pau":
            phrase_len.append("null")
            accent_idx.append("null")
            continue
        p = re.findall(r"F:([0-9]+)_([0-9]+).*?@([0-9]+)_", labels)
        if len(p) == 1:
            if prev != p[0][2] :
                phrase_len.append(int(p[0][0]))
                accent_idx.append(int(p[0][1]))
            prev=p[0][2]
    left=0
    phrase=[]
    for idx in phrase_len:
        if idx != "null":
            phrase += [mora[left:left+idx]]
            left+=idx
        else :
            phrase += [''.join(mora[left:left+1])]
            left+=1
    
    return phrase,phrase_len,accent_idx

def text2yomi(text):
    accented=""
    ap=accent_phrase(text)
    for i,phrase_mora in enumerate(ap[0]):
        if ap[1][i] == "null":
            accented += ''.join(phrase_mora)
            accented+=" "
        else:
            phrase = phrase_mora[:ap[2][i]]
            phrase += '^'
            phrase += phrase_mora[ap[2][i]:]

            accented+=''.join(phrase)
            accented+=" "
    
    yomi = jaconv.kata2hira(accented[0:-1])
    
    return yomi

def a2p(accented):
    phonemes = np.empty(0)
    print("アクセント句分割：")
    print(accented.split('　'))
    print("\n")
    for phrase in accented.split('　'):
        
        mora = moraWakachi( jaconv.hira2kata(phrase) )

        if '^' in mora : 
            nucleus = mora.index('^')
            mora.remove('^')
            plane_text = phrase.replace('^','')
        elif '＾' in mora :
            nucleus = mora.index('＾')
            mora.remove('＾')
            plane_text = phrase.replace('＾','')
        else : 
            phonemes = np.append(phonemes,'pau')
            continue

        n_mora = len(mora)

        distances = np.arange(1,n_mora+1) - nucleus
        distances = distances.reshape(-1,1)

        nucleuses = np.array(nucleus)
        nucleuses = np.tile(nucleuses , (n_mora,1))

        nuc_dist=np.hstack([nucleuses , distances])
        #print(nuc_dist)
    
        phrase_phonemes = np.empty(0)
        mora_idx = np.empty(0)
        prev_idx=0
        i = 0
        print("モーラ分割：")
        print(mora)
        print("\n")
        
        print("音素 , アクセント核の位置(モーラ単位) , アクセント核からの距離(モーラ単位)：")
        for labels in pyopenjtalk.run_frontend(plane_text)[1]:
            if labels.split("-")[1].split("+")[0] == "pau":
                continue
            p = re.findall(r"\-(.*?)\+.*?\/A:[0-9\-]+\+([0-9\-]+)", labels)
            if len(p) == 1:
                print(p[0][0] , end=' , ')
                phrase_phonemes = np.append(phrase_phonemes , p[0][0])
                idx = int(p[0][1]) - 1
                if idx != prev_idx :
                    i += 1
                    prev_idx = idx
                print(nuc_dist[i])
                
                phrase_phonemes = np.append(phrase_phonemes , nuc_dist[i])
                
        print("\n")
        phonemes = np.append(phonemes , phrase_phonemes)
        #print(phonemes)
    return phonemes


