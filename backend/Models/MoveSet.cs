using System;
using System.Collections.Generic;
using System.Linq;

namespace backend
{
    public class MoveSet
    {
        public class Move
        {
            public string ResultingFEN { get; set; }
            public string StartPos { get; set; }
            public string EndPos { get; set; }
            public int TimesPlayed { get; set; }
        }
        private Dictionary<string, int> _MoveFrequencyMap;
        private Dictionary<string, MatchHistory.Move> _MoveInfoMap;

        public MoveSet()
        {
            _MoveFrequencyMap = new Dictionary<string, int>();
            _MoveInfoMap = new Dictionary<string, MatchHistory.Move>();
        }
        public MoveSet LoadMoves(string fen)
        {
            MatchHistory.BoardState boardState;
            bool boardExists = MatchHistory.Singleton.GetBoardStateFromFEN(fen, out boardState);

            if (boardExists)
            {
                _MoveFrequencyMap.Clear();

                foreach (MatchHistory.Move possibility in boardState.PossibleMoves)
                {
                    _MoveInfoMap.Add(possibility.Description, possibility);
                    if (_MoveFrequencyMap.ContainsKey(possibility.Description))
                    {
                        _MoveFrequencyMap[possibility.Description] += 1;
                    }
                    else
                    {
                        _MoveFrequencyMap.Add(possibility.Description, 1);
                    }
                    
                }
            }

            return this;
        }

        public IEnumerable<Move> GetRankedMoves()
        {
            var moveList = _MoveFrequencyMap.ToList();
            moveList.Sort(
                (pair1, pair2) => pair1.Value.CompareTo(pair2.Value)
            );

            return moveList.Select(
                (pair) => {
                    var moveInfo = _MoveInfoMap[pair.Key];
                    return new Move {
                        ResultingFEN = moveInfo.ResultingFEN,
                        StartPos = moveInfo.Action.Item1,
                        EndPos = moveInfo.Action.Item2,
                        TimesPlayed = pair.Value
                    };
                }
            );
        }
    }
}