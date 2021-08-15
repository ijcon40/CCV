using System;
using System.Collections.Generic;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace backend
{
    public class MatchHistory
    {
        public class Move
        {
            public string Description { get; set; }
            public string ResultingFEN { get; set; }
            public Tuple<string, string> Action { get; set; }
        }
        public class BoardState
        {
            public string FEN { get; set; }
            public List<string> RelatedMatches { get; set; }
            public List<Move> PossibleMoves { get; set; }

            public BoardState()
            {
                RelatedMatches = new List<string>();
                PossibleMoves = new List<Move>();
            }

            public BoardState(string fen, JObject jsonObj)
                : this()
            {
                var games = jsonObj["games"].ToObject<List<string>>();
                var movesDict = jsonObj["moves"].ToObject<Dictionary<string, string>>();

                FEN = fen;
                RelatedMatches = games;
                foreach (KeyValuePair<string, string> entry in movesDict)
                {
                    string startPos = entry.Value.Substring(0, 2);
                    string endPos = entry.Value.Substring(2, 2);

                    PossibleMoves.Add(new Move {
                        Description = entry.Value,
                        ResultingFEN = entry.Key,
                        Action = new Tuple<string, string>(startPos, endPos)
                    });
                }
            }

        }

        private Dictionary<string, BoardState> _RecordedStates;

        public static MatchHistory Singleton = new MatchHistory();

        public MatchHistory()
        {
            _RecordedStates = new Dictionary<string, BoardState>();
            InitFromJSON("./data/tmp-data.json");
        }

        public bool GetBoardStateFromFEN(string fenCode, out BoardState retrievedState)
        {
            return _RecordedStates.TryGetValue(fenCode, out retrievedState);
        }

        private void InitFromJSON(string pathToJSON)
        {
            string jsonText = System.IO.File.ReadAllText(pathToJSON);
            var jsonDict = JsonConvert.DeserializeObject<Dictionary<string, JObject>>(jsonText);
            
            foreach (KeyValuePair<string, JObject> entry in jsonDict)
            {
                var fenCode = entry.Key;
                var jsonObj = entry.Value;
                
                _RecordedStates.Add(fenCode, new BoardState(fenCode, jsonObj));
            }
        }
    }
}