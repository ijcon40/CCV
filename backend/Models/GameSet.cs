using System;
using System.Collections.Generic;

namespace backend
{
    public class GameSet
    {
        public class Match
        {
            public string Title { get; set; }
            public string PlayerA { get; set; }
            public string PlayerB { get; set; }
        }

        private List<Match> _Matches;
        public GameSet()
        {
            _Matches = new List<Match>();
        }

        public GameSet LoadMatches(string fen)
        {
            MatchHistory.BoardState boardState;
            bool boardExists = MatchHistory.Singleton.GetBoardStateFromFEN(fen, out boardState);

            if (boardExists)
            {
                _Matches.Clear();
                foreach (string match in boardState.RelatedMatches)
                {
                    var idxTitleEnd = match.IndexOf(']');
                    var idxPlayerABegin = idxTitleEnd+2;
                    var idxPlayerAEnd = match.LastIndexOf(" vs. ");
                    var idxPlayerBBegin = idxPlayerAEnd+5;
                    var idxPlayerBEnd = match.Length - 1;

                    string title = match.Substring(1, idxTitleEnd-1);
                    string playerA = match.Substring(idxPlayerABegin, idxPlayerAEnd-idxPlayerABegin);
                    string playerB = match.Substring(idxPlayerBBegin, idxPlayerBEnd-idxPlayerBBegin+1);

                    _Matches.Add(new Match {
                        Title = title,
                        PlayerA = playerA,
                        PlayerB = playerB
                    });
                }
            }
            
            return this;
        }

        public IEnumerable<Match> GetMatches()
        {
            return _Matches;
        }
    }
}