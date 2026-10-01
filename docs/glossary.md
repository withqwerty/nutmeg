# Glossary

Short meanings for the football analytics terms nutmeg uses. The workspace page links a term to its entry on the
term's first use in each section. Each entry is a `##` heading, an `Aliases:` line (the words that link to it) and
its meaning. This list does not grow with new metric definitions: provider-specific definitions come from
football-docs, and project-specific definitions are `definition` claims in the ledger.

## xG (expected goals)
Aliases: xG, expected goals
The probability that a shot results in a goal, from 0 to 1. Intuition: how good was the chance? Models differ by
provider, so name the model.

## npxG (non-penalty expected goals)
Aliases: npxG, non-penalty xG, non-penalty expected goals
xG without penalties. Penalties are high-value chances that few players take, so they distort per-player
comparisons.

## xGOT (expected goals on target)
Aliases: xGOT, xG on target, PSxG, post-shot xG, post-shot expected goals
xG adjusted for where the shot went in the goal. Intuition: how good was the finish? PSxG is the same idea in
StatsBomb's terms.

## xA (expected assists)
Aliases: xA, expected assists
The xG of the shot that a pass led to. Intuition: how good was the chance created?

## xT (expected threat)
Aliases: xT, expected threat
The value added by moving the ball to a more dangerous area. Intuition: how much did this pass or carry raise the
chance of a goal? Introduced by Karun Singh.

## PPDA (passes allowed per defensive action)
Aliases: PPDA, passes allowed per defensive action
Opponent passes allowed per defensive action in a defined area. Lower means more intense pressing.

## High press
Aliases: high press, high pressing
Defensive actions in the opponent's defensive third.

## Counterpressure
Aliases: counterpressure, counter-press, counterpress, gegenpress
An immediate defensive reaction after losing the ball.

## Build-up
Aliases: build-up, build up, buildup
How a team moves the ball from defence to attack.

## Possession value
Aliases: possession value, possession-value
How much each action adds to the chance of scoring (and of conceding). xT and VAEP are possession value models.

## Progressive pass
Aliases: progressive pass, progressive passes
A pass that moves the ball a long way towards the opponent's goal. Providers define the distance differently.

## Progressive carry
Aliases: progressive carry, progressive carries
A carry that moves the ball a long way towards the opponent's goal. Providers define the distance differently.

## Key pass
Aliases: key pass, key passes
A pass that leads directly to a shot.

## Assist
Aliases: assist, assists
A pass that leads directly to a goal.

## Through ball
Aliases: through ball, through balls
A pass into space behind the defence.

## Switch of play
Aliases: switch of play, switches of play
A long pass across the centre of the pitch.

## Pass completion
Aliases: pass completion, pass completion %, pass accuracy
Successful passes divided by all passes. Misleading on its own: it rewards safe passes.

## Shots per 90
Aliases: shots per 90
Shot volume per 90 minutes played.

## Conversion rate
Aliases: conversion rate, shot conversion
Goals divided by shots. Noisy: one season is too small a sample to judge finishing.

## Big chance
Aliases: big chance, big chances
A chance an analyst judges the player should reasonably score. A coded label, not an xG threshold; check the
provider's definition in football-docs.

## Shot on target %
Aliases: shots on target %, shot on target %, on-target %
Shots on target divided by all shots.

## Tackles won
Aliases: tackles won
Successful tackle attempts. Count them per possession (possession-adjusted), not raw.

## Interceptions
Aliases: interception, interceptions
Passes read and intercepted.

## Clearances
Aliases: clearance, clearances
Defensive clearances, often under pressure.

## Blocks
Aliases: block, blocks
Shots or passes blocked.

## Aerial duels won
Aliases: aerial duels won, aerials won
Headers contested and won.

## Per 90
Aliases: per 90, per-90, p90
A count divided by minutes played, times 90. It removes the effect of playing time. Use a minimum-minutes filter
(about 900 minutes is a common rule of thumb).
