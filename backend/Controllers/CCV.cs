using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace backend.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class CCV : ControllerBase
    {
        public class Recommendation
        {
            public IEnumerable<GameSet.Match> RelatedMatches { get; set; }
            public IEnumerable<MoveSet.Move> RecommendedMoves { get; set; }
        }
        private readonly ILogger<CCV> _logger;

        public CCV(ILogger<CCV> logger)
        {
            _logger = logger;
        }

        [HttpGet]
        public ActionResult<Recommendation> Get(string state)
        {
            if (state == null)
            {
                Console.WriteLine("Board state is null");
                return NotFound();
            }
            
            Console.WriteLine($"Searching for board state \"{state}\"");

            var relatedMatches = new GameSet().LoadMatches(state).GetMatches();
            var possibleMoves = new MoveSet().LoadMoves(state).GetRankedMoves();

            if (relatedMatches.Count() == 0 || possibleMoves.Count() == 0)
            {
                Console.WriteLine($"Board state \"{state}\" does not exist");
                return NotFound();
            }

            return new Recommendation {
                RelatedMatches = relatedMatches, 
                RecommendedMoves = possibleMoves
            };
        }
    }
}
