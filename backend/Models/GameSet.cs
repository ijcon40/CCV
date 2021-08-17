using System;
using System.Collections.Generic;

namespace backend
{
    public class GameSet
    {
        public class Match
        {
            public string Title { get; set; }
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
                    if (match.Length > 0)
                    {
                        _Matches.Add(new Match {
                            Title = match,
                        });
                    }
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