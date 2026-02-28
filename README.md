# Jak spustit?

```
py run_experiment.py --games 100 --threads 4
```

# Kde jsou statistiky?

Statistiky jsou vyobrazené v grafech v `plot_results.ipynb`.

# Výsledky meření

Při měření bylo provedeno 100 her pro každý algoritmus. U algoritmů Minimax a Expectiminimax byly testovány hloubky 1, 2 a 3.
K evaluaci skóre byla použita tzv. [snake-heuristics](https://cs229.stanford.edu/proj2016/report/NieHouAn-AIPlays2048-report.pdf).
Z grafů je patrné, že nejlepšího výkonu dosahuje algoritmus Expectiminimax s hloubkou 3.
